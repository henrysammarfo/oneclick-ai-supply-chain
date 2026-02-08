"""SQLite database operations for agent registry."""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from loguru import logger

Base = declarative_base()


class AgentTable(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(64), unique=True, nullable=False, index=True)
    role = Column(String(32), nullable=False, index=True)
    capabilities = Column(Text, default="[]")
    endpoint = Column(String(256), default="")
    jurisdiction = Column(String(64), default="global")
    status = Column(String(16), default="active")
    performance_score = Column(Float, default=1.0)
    total_transactions = Column(Integer, default=0)
    registered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseManager:
    """Manages SQLite database for agent registry."""

    def __init__(self, db_url: str = "sqlite:///agent_registry.db"):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)
        logger.info("Database initialized")

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def insert_agent(self, agent_data: Dict[str, Any]) -> bool:
        with self._get_session() as session:
            try:
                row = AgentTable(
                    agent_id=agent_data["agent_id"],
                    role=agent_data["role"],
                    capabilities=json.dumps(agent_data.get("capabilities", [])),
                    endpoint=agent_data.get("endpoint", ""),
                    jurisdiction=agent_data.get("jurisdiction", "global"),
                    status=agent_data.get("status", "active"),
                    performance_score=agent_data.get("performance_score", 1.0),
                )
                session.add(row)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Insert failed: {e}")
                return False

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        with self._get_session() as session:
            row = session.query(AgentTable).filter_by(agent_id=agent_id).first()
            return self._row_to_dict(row) if row else None

    def query_agents(
        self,
        role: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        jurisdiction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self._get_session() as session:
            q = session.query(AgentTable).filter_by(status="active")
            if role:
                q = q.filter_by(role=role)
            if jurisdiction:
                q = q.filter_by(jurisdiction=jurisdiction)
            results = q.all()
            agents = [self._row_to_dict(r) for r in results]
            if capabilities:
                agents = [
                    a for a in agents
                    if any(c in a.get("capabilities", []) for c in capabilities)
                ]
            return agents

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        with self._get_session() as session:
            try:
                row = session.query(AgentTable).filter_by(agent_id=agent_id).first()
                if not row:
                    return False
                for key, val in updates.items():
                    if key == "capabilities":
                        val = json.dumps(val)
                    if hasattr(row, key):
                        setattr(row, key, val)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Update failed: {e}")
                return False

    def delete_agent(self, agent_id: str) -> bool:
        with self._get_session() as session:
            try:
                row = session.query(AgentTable).filter_by(agent_id=agent_id).first()
                if row:
                    session.delete(row)
                    session.commit()
                    return True
                return False
            except Exception as e:
                session.rollback()
                logger.error(f"Delete failed: {e}")
                return False

    def get_all_agents(self) -> List[Dict[str, Any]]:
        with self._get_session() as session:
            rows = session.query(AgentTable).all()
            return [self._row_to_dict(r) for r in rows]

    @staticmethod
    def _row_to_dict(row: AgentTable) -> Dict[str, Any]:
        return {
            "agent_id": row.agent_id,
            "role": row.role,
            "capabilities": json.loads(row.capabilities or "[]"),
            "endpoint": row.endpoint,
            "jurisdiction": row.jurisdiction,
            "status": row.status,
            "performance_score": row.performance_score,
            "total_transactions": row.total_transactions,
            "registered_at": str(row.registered_at),
        }
