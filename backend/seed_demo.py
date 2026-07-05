"""
Pre-loads the scripted 4-session scenario from DEMO_SCRIPT.md straight into
Cognee. Run this once before judging so that even if live typing goes
sideways, you can fall back to asking the exact scripted follow-up questions
and still get the payoff answers.

Usage:
    python seed_demo.py
"""

import asyncio

import cognee
from dotenv import load_dotenv

load_dotenv()

CUSTOMER_ID = "priya_4471"

SESSION_1 = [
    "Customer said: Hi, I'm Priya. My order #4471 arrived damaged — the "
    "packaging was crushed and one item was broken.",
    "Nova replied: I'm sorry about that, Priya. I've logged order #4471 as "
    "damaged in transit and started a replacement.",
]

SESSION_2 = [
    "Customer said: Hey, following up on my order — any update?",
    "Nova replied: Your replacement for order #4471 shipped yesterday and "
    "should arrive Friday.",
]

SESSION_3 = [
    "Customer said: By the way, if this happens again, can you ship future "
    "orders in extra padding?",
    "Nova replied: Done — I've flagged your account for reinforced "
    "packaging on all future shipments, since order #4471 arrived damaged.",
]

# A second customer, same root cause, so the graph-only question in
# Session 4 has something real to traverse.
OTHER_CUSTOMER_ID = "marcus_5190"
OTHER_CUSTOMER_SESSION = [
    "Customer said: Order #5190 showed up with a cracked case, packaging "
    "was crushed too.",
    "Nova replied: I'm sorry, Marcus. Order #5190 is flagged as damaged in "
    "transit — root cause traced to a mis-packing issue at Warehouse B this "
    "week. Replacement is on the way.",
]


async def seed():
    print("Resetting memory...")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    for label, turns in [
        ("Session 1 (Priya)", SESSION_1),
        ("Session 2 (Priya)", SESSION_2),
        ("Session 3 (Priya)", SESSION_3),
        ("Other customer (Marcus)", OTHER_CUSTOMER_SESSION),
    ]:
        print(f"Writing {label}...")
        session_id = OTHER_CUSTOMER_ID if "Marcus" in label else CUSTOMER_ID
        for turn in turns:
            await cognee.remember(turn, session_id=session_id)

    print("Done. Try recalling with:")
    print(f'  await cognee.recall("any update on my order?", session_id="{CUSTOMER_ID}")')


if __name__ == "__main__":
    asyncio.run(seed())
