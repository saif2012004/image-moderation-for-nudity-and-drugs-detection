#!/usr/bin/env python3
"""
Database Backup Script for Image Moderation API
Automated backup and restoration of MongoDB data
"""

import subprocess
import datetime
import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
BACKUP_DIR = "backups"
DB_NAME = "image_moderation"
CONTAINER_NAME = "image_moderation_mongodb"
RETENTION_DAYS = 30
MAX_BACKUPS = 50

class DatabaseBackup:
    def __init__(self):
        self.backup_dir = Path(BACKUP_DIR)
        self.backup_dir.mkdir(exist_ok=True)
        
    def check_docker_running(self) -> bool:
        """Check if Docker is running"""
        try:
            result = subprocess.run(["docker", "info"], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_mongodb_container(self) -> bool:
        """Check if MongoDB container is running"""
        try:
            result = subprocess.run([
                "docker", "ps", "--filter", f"name={CONTAINER_NAME}", 
                "--format", "{{.Names}}"
            ], capture_output=True, text=True, check=True)
            
            return CONTAINER_NAME in result.stdout.strip()
        except subprocess.CalledProcessError:
            return False
    
    def create_backup(self) -> Dict[str, str]:
        """Create a new database backup"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"db_backup_{timestamp}.archive"
        metadata_file = self.backup_dir / f"db_backup_{timestamp}.json"
        
        print(f"🗄️  Creating database backup: {backup_file.name}")
        
        try:
            # Create MongoDB dump
            dump_cmd = [
                "docker", "exec", CONTAINER_NAME,
                "mongodump", "--db", DB_NAME, "--archive"
            ]
            
            with open(backup_file, "wb") as f:
                result = subprocess.run(dump_cmd, stdout=f, stderr=subprocess.PIPE, check=True)
            
            # Get database stats
            stats = self.get_database_stats()
            
            # Create metadata
            metadata = {
                "timestamp": timestamp,
                "database": DB_NAME,
                "backup_file": backup_file.name,
                "size_bytes": backup_file.stat().st_size,
                "size_mb": round(backup_file.stat().st_size / (1024 * 1024), 2),
                "created_at": datetime.datetime.now().isoformat(),
                "stats": stats
            }
            
            # Save metadata
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Backup created successfully!")
            print(f"   • File: {backup_file.name}")
            print(f"   • Size: {metadata['size_mb']} MB")
            print(f"   • Collections: {len(stats.get('collections', []))}")
            
            return {
                "success": True,
                "backup_file": str(backup_file),
                "metadata_file": str(metadata_file),
                "metadata": metadata
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            print(f"❌ Backup failed: {error_msg}")
            
            # Cleanup partial files
            if backup_file.exists():
                backup_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
                
            return {"success": False, "error": error_msg}
        
        except Exception as e:
            print(f"❌ Backup failed with unexpected error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def restore_backup(self, backup_file: str) -> Dict[str, str]:
        """Restore database from backup"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return {"success": False, "error": f"Backup file not found: {backup_file}"}
        
        print(f"🔄 Restoring database from: {backup_path.name}")
        print("⚠️  This will replace all existing data!")
        
        # Confirm restoration
        if not self._confirm_restore():
            return {"success": False, "error": "Restoration cancelled by user"}
        
        try:
            # Restore MongoDB dump
            restore_cmd = [
                "docker", "exec", "-i", CONTAINER_NAME,
                "mongorestore", "--db", DB_NAME, "--archive", "--drop"
            ]
            
            with open(backup_path, "rb") as f:
                result = subprocess.run(restore_cmd, stdin=f, 
                                      capture_output=True, text=True, check=True)
            
            print("✅ Database restored successfully!")
            print(f"   • From: {backup_path.name}")
            print(f"   • Size: {round(backup_path.stat().st_size / (1024 * 1024), 2)} MB")
            
            return {"success": True, "backup_file": str(backup_path)}
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            print(f"❌ Restoration failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        except Exception as e:
            print(f"❌ Restoration failed with unexpected error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("db_backup_*.archive"):
            metadata_file = backup_file.with_suffix(".json")
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                    backups.append(metadata)
                except json.JSONDecodeError:
                    # Create basic metadata if file is corrupted
                    stat = backup_file.stat()
                    backups.append({
                        "timestamp": backup_file.stem.replace("db_backup_", ""),
                        "backup_file": backup_file.name,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "metadata_corrupted": True
                    })
            else:
                # Create basic metadata for files without metadata
                stat = backup_file.stat()
                backups.append({
                    "timestamp": backup_file.stem.replace("db_backup_", ""),
                    "backup_file": backup_file.name,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "no_metadata": True
                })
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return backups
    
    def cleanup_old_backups(self) -> Dict[str, int]:
        """Remove old backups based on retention policy"""
        print(f"🧹 Cleaning up old backups (retention: {RETENTION_DAYS} days, max: {MAX_BACKUPS})")
        
        removed_count = 0
        total_size_freed = 0
        
        # Get all backups
        backups = self.list_backups()
        
        # Remove by age
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
        
        for backup in backups:
            try:
                backup_date = datetime.datetime.fromisoformat(backup["created_at"])
                if backup_date < cutoff_date:
                    self._remove_backup(backup["backup_file"])
                    removed_count += 1
                    total_size_freed += backup.get("size_mb", 0)
                    print(f"   Removed old backup: {backup['backup_file']}")
            except (ValueError, KeyError):
                # Skip backups with invalid dates
                continue
        
        # Remove excess backups (keep only MAX_BACKUPS newest)
        if len(backups) > MAX_BACKUPS:
            excess_backups = backups[MAX_BACKUPS:]
            for backup in excess_backups:
                self._remove_backup(backup["backup_file"])
                removed_count += 1
                total_size_freed += backup.get("size_mb", 0)
                print(f"   Removed excess backup: {backup['backup_file']}")
        
        print(f"✅ Cleanup completed: {removed_count} backups removed, {total_size_freed:.2f} MB freed")
        
        return {
            "removed_count": removed_count,
            "size_freed_mb": total_size_freed
        }
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            # Get collection stats
            stats_cmd = [
                "docker", "exec", CONTAINER_NAME,
                "mongosh", "--quiet", "--eval",
                f"db = db.getSiblingDB('{DB_NAME}'); "
                "print(JSON.stringify({collections: db.getCollectionNames(), "
                "stats: db.stats()}))"
            ]
            
            result = subprocess.run(stats_cmd, capture_output=True, text=True, check=True)
            stats = json.loads(result.stdout.strip())
            
            return stats
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return {"error": "Could not retrieve database stats"}
    
    def _remove_backup(self, backup_file: str):
        """Remove a backup file and its metadata"""
        backup_path = self.backup_dir / backup_file
        metadata_path = backup_path.with_suffix(".json")
        
        if backup_path.exists():
            backup_path.unlink()
        if metadata_path.exists():
            metadata_path.unlink()
    
    def _confirm_restore(self) -> bool:
        """Ask user to confirm restoration"""
        try:
            response = input("Are you sure you want to restore? This will delete existing data. (yes/no): ")
            return response.lower() in ["yes", "y"]
        except KeyboardInterrupt:
            return False

def main():
    """Main backup script execution"""
    if len(sys.argv) < 2:
        print("Usage: python backup.py [create|restore|list|cleanup]")
        print("  create  - Create a new backup")
        print("  restore <backup_file> - Restore from backup")
        print("  list    - List all backups")
        print("  cleanup - Remove old backups")
        sys.exit(1)
    
    action = sys.argv[1]
    backup = DatabaseBackup()
    
    # Check prerequisites
    if not backup.check_docker_running():
        print("❌ Docker is not running")
        sys.exit(1)
    
    if not backup.check_mongodb_container():
        print(f"❌ MongoDB container '{CONTAINER_NAME}' is not running")
        sys.exit(1)
    
    try:
        if action == "create":
            result = backup.create_backup()
            sys.exit(0 if result["success"] else 1)
            
        elif action == "restore":
            if len(sys.argv) < 3:
                print("Usage: python backup.py restore <backup_file>")
                sys.exit(1)
            
            backup_file = sys.argv[2]
            result = backup.restore_backup(backup_file)
            sys.exit(0 if result["success"] else 1)
            
        elif action == "list":
            backups = backup.list_backups()
            if not backups:
                print("No backups found")
            else:
                print(f"📋 Found {len(backups)} backups:")
                print("-" * 80)
                for b in backups:
                    created = b["created_at"][:19].replace("T", " ")
                    print(f"  {b['backup_file']:<30} {b['size_mb']:>8.2f} MB  {created}")
                    
        elif action == "cleanup":
            backup.cleanup_old_backups()
            
        else:
            print(f"Unknown action: {action}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚡ Operation interrupted")
        sys.exit(2)
    except Exception as e:
        print(f"💥 Operation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 