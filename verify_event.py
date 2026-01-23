
from src.models import User, Event, UserEvent
from src.main import check_global_events
from sqlmodel import Session, create_engine, SQLModel
from unittest.mock import MagicMock, patch
import src.content_manager as cm

# Setup In-Memory DB
engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

def test_event_trigger():
    with Session(engine) as session:
        # Create User
        user = User(username="test_user")
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Mock ContentManager.get_events
        mock_event = Event(id="evt_1", type="dialogue", conditions="first_view", content="foo.yaml")
        
        with patch("src.content_manager.ContentManager.get_events", return_value=[mock_event]):
            # 1. First check: Should return event
            evt = check_global_events(user, session)
            assert evt is not None
            assert evt.id == "evt_1"
            print("✅ TEST 1 PASSED: Event triggered on first view")
            
            # Simulate trigger (create UserEvent)
            ue = UserEvent(user_id=user.id, event_id=evt.id, timestamp=0.0)
            session.add(ue)
            session.commit()
            
            # 2. Second check: Should return None
            evt2 = check_global_events(user, session)
            assert evt2 is None
            print("✅ TEST 2 PASSED: Event not triggered on second view")

if __name__ == "__main__":
    test_event_trigger()
