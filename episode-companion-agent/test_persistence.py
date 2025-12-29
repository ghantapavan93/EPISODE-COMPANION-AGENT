"""
Test script to verify SQLite state persistence works correctly.
"""
from database import SessionLocal, Base, engine
from conversation_manager import ConversationManager
from models import Conversation, Message

# Create tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✓ Database tables created")

# Test 1: Create a conversation
print("\n Test 1: Creating conversation...")
db = SessionLocal()
manager = ConversationManager(db)

manager.add_turn(
    user_id="test_user",
    episode_id="ai-research-daily-2025-11-18",
    query="What is Kandinsky 5.0?",
    answer="Kandinsky 5.0 is a real-time video generation model...",
    mode="plain_english",
    meta={"latency_ms": 1200, "used_chunks": 5}
)

print("✓ Added first turn")

# Test 2: Add another turn
manager.add_turn(
    user_id="test_user",
    episode_id="ai-research-daily-2025-11-18",
    query="How fast is it?",
    answer="It generates at 30fps in real-time.",
    mode="plain_english",
    meta={"latency_ms": 800, "used_chunks": 3}
)

print("✓ Added second turn")

# Test 3: Retrieve conversation history
history = manager.get_context_string("test_user", "ai-research-daily-2025-11-18")
print(f"\n📜 Retrieved history:\n{history}")

# Test 4: Get last episode ID
last_episode = manager.get_last_episode_id("test_user")
print(f"\n✓ Last episode ID: {last_episode}")

# Test 5: Close and reopen session (simulating server restart)
db.close()
print("\n✓ Closed session (simulating restart)")

db2 = SessionLocal()
manager2 = ConversationManager(db2)

history2 = manager2.get_context_string("test_user", "ai-research-daily-2025-11-18")
print(f"\n📜 Retrieved history after 'restart':\n{history2}")

# Test 6: Check that data persisted
assert history == history2, "History should persist across sessions!"
print("\n✅ PERSISTENCE TEST PASSED! Data survives session restarts.")

db2.close()

print("\n🎉 All tests passed! SQLite state persistence is working correctly.")
