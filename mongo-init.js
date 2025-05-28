// MongoDB Initialization Script for Image Moderation API
// This script runs when the MongoDB container starts for the first time

print("===========================================");
print("Image Moderation API - Database Setup");
print("===========================================");

// Switch to the image_moderation database
db = db.getSiblingDB("image_moderation");

// Create the tokens collection and insert initial admin token
print("Creating tokens collection...");
db.tokens.insertOne({
  token: "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA",
  isAdmin: true,
  createdAt: new Date(),
  lastUsed: new Date(),
  usageCount: 0,
  active: true,
});

// Create indexes for better performance
print("Creating indexes...");

// Index on token field for faster lookups
db.tokens.createIndex({ token: 1 }, { unique: true });

// Index on createdAt for cleanup operations
db.tokens.createIndex({ createdAt: 1 });

// Index on lastUsed for analytics
db.tokens.createIndex({ lastUsed: 1 });

// Index on active status
db.tokens.createIndex({ active: 1 });

// Create moderation_logs collection for tracking API usage
print("Creating moderation_logs collection...");
db.moderation_logs.createIndex({ timestamp: 1 });
db.moderation_logs.createIndex({ token: 1 });
db.moderation_logs.createIndex({ filename: 1 });
db.moderation_logs.createIndex({ safe: 1 });

// Create admin user for the database
print("Creating database user...");
db.createUser({
  user: "api_user",
  pwd: "api_password_123",
  roles: [
    {
      role: "readWrite",
      db: "image_moderation",
    },
  ],
});

// Verify setup
print("Verifying setup...");
print("Tokens count:", db.tokens.countDocuments());
print(
  "Admin token exists:",
  db.tokens.findOne({
    token: "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA",
  }) !== null
);

print("===========================================");
print("Database initialization completed!");
print("Admin Token: BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA");
print("===========================================");
