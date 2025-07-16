#!/usr/bin/env python3
"""
Script to create the JWT blacklist table manually if migrations don't work.
Run this from the Mage AI root directory.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

try:
    from mage_ai.orchestration.db import db_connection
    from sqlalchemy import (
        Column, DateTime, Integer, String, Text, Index, 
        MetaData, Table, create_engine
    )
    
    def create_jwt_blacklist_table():
        """Create the JWT blacklist table manually."""
        
        print("Connecting to database...")
        
        # Get the database connection
        engine = db_connection.engine
        metadata = MetaData()
        
        # Check if table already exists
        metadata.reflect(bind=engine)
        if 'jwt_blacklist' in metadata.tables:
            print("JWT blacklist table already exists!")
            return True
        
        print("Creating JWT blacklist table...")
        
        # Define the table structure
        jwt_blacklist_table = Table(
            'jwt_blacklist',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('created_at', DateTime(timezone=True), server_default='now()'),
            Column('updated_at', DateTime(timezone=True), server_default='now()'),
            Column('token', Text, nullable=False, unique=True, index=True),
            Column('jti', String(255), nullable=True, index=True),
            Column('blacklisted_at', DateTime(timezone=True), nullable=False),
            Column('expires_at', DateTime(timezone=True), nullable=False),
            Column('reason', String(255), nullable=True),
            
            # Indexes
            Index('idx_jwt_blacklist_expires_at', 'expires_at'),
            Index('idx_jwt_blacklist_token_expires', 'token', 'expires_at'),
        )
        
        # Create the table
        jwt_blacklist_table.create(engine)
        
        print("JWT blacklist table created successfully!")
        return True
        
    if __name__ == "__main__":
        try:
            success = create_jwt_blacklist_table()
            if success:
                print("\n✅ JWT blacklist functionality is now ready!")
                print("You can now:")
                print("1. Check token blacklist status using: JWTBlacklist.is_token_blacklisted(token)")
                print("2. Blacklist tokens on logout")
                print("3. Benefit from enhanced session security")
            else:
                print("❌ Failed to create JWT blacklist table")
                
        except Exception as e:
            print(f"❌ Error creating JWT blacklist table: {e}")
            print("Please check your database connection and permissions.")
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this from the Mage AI root directory.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")