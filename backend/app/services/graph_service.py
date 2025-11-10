"""
Сервис графа связей (Neo4j)
"""
import logging
from typing import List, Dict, Optional
from neo4j import GraphDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)


class GraphService:
    """Сервис для работы с графовой БД Neo4j"""
    
    def __init__(self):
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Подключение к Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # Проверка соединения
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")
        except Exception as e:
            logger.error(f"Error connecting to Neo4j: {e}")
            logger.warning("Graph features will be unavailable")
            self.driver = None
    
    def _get_session(self):
        """Получение сессии Neo4j"""
        if self.driver is None:
            return None
        return self.driver.session()
    
    async def create_node(
        self,
        node_id: str,
        node_type: str,
        properties: Dict
    ):
        """
        Создание узла в графе
        
        Args:
            node_id: Уникальный ID узла
            node_type: Тип узла (class, function, file, etc.)
            properties: Свойства узла
        """
        if self.driver is None:
            return
        
        try:
            with self._get_session() as session:
                query = f"""
                MERGE (n:{node_type} {{id: $id}})
                SET n += $properties
                """
                session.run(query, id=node_id, properties=properties)
                logger.debug(f"Created node: {node_id}")
        except Exception as e:
            logger.error(f"Error creating node {node_id}: {e}")
    
    async def create_relationship(
        self,
        from_id: str,
        to_id: str,
        relation_type: str,
        project_id: str,
        properties: Optional[Dict] = None
    ):
        """
        Создание связи между узлами
        
        Args:
            from_id: ID исходного узла
            to_id: ID целевого узла
            relation_type: Тип связи (references, depends_on, etc.)
            project_id: ID проекта
            properties: Дополнительные свойства связи
        """
        if self.driver is None:
            return
        
        try:
            with self._get_session() as session:
                query = """
                MATCH (a {id: $from_id})
                MATCH (b {id: $to_id})
                MERGE (a)-[r:RELATES_TO {type: $relation_type, project_id: $project_id}]->(b)
                """
                params = {
                    "from_id": from_id,
                    "to_id": to_id,
                    "relation_type": relation_type,
                    "project_id": project_id
                }
                if properties:
                    query = query.replace("}]->", "}]->")
                    # Добавление свойств связи
                    for key, value in properties.items():
                        query += f" SET r.{key} = ${key}"
                        params[key] = value
                
                session.run(query, **params)
                logger.debug(f"Created relationship: {from_id} -> {to_id} ({relation_type})")
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
    
    async def get_entity_graph(
        self,
        entity_id: str,
        depth: int = 2,
        max_nodes: int = 50
    ) -> Dict:
        """
        Получить граф для сущности
        
        Args:
            entity_id: ID сущности
            depth: Глубина обхода
            max_nodes: Максимальное количество узлов
        
        Returns:
            Граф с узлами и связями
        """
        if self.driver is None:
            return {"nodes": [], "edges": []}
        
        try:
            with self._get_session() as session:
                query = f"""
                MATCH path = (start {{id: $entity_id}})-[*1..{depth}]-(connected)
                WHERE start.id = $entity_id
                WITH path, relationships(path) as rels
                UNWIND rels as rel
                WITH DISTINCT start, connected, rel
                LIMIT {max_nodes}
                RETURN start, connected, rel
                """
                
                result = session.run(query, entity_id=entity_id, max_nodes=max_nodes)
                
                nodes = {}
                edges = []
                
                for record in result:
                    start_node = record["start"]
                    connected_node = record["connected"]
                    relationship = record["rel"]
                    
                    # Добавление узлов
                    nodes[start_node.id] = {
                        "id": start_node.id,
                        "type": list(start_node.labels)[0] if start_node.labels else "Unknown",
                        "label": start_node.get("name", start_node.id),
                        "properties": dict(start_node)
                    }
                    
                    nodes[connected_node.id] = {
                        "id": connected_node.id,
                        "type": list(connected_node.labels)[0] if connected_node.labels else "Unknown",
                        "label": connected_node.get("name", connected_node.id),
                        "properties": dict(connected_node)
                    }
                    
                    # Добавление связи
                    edges.append({
                        "source": start_node.id,
                        "target": connected_node.id,
                        "type": relationship.get("type", "RELATES_TO"),
                        "weight": relationship.get("weight", 1.0),
                        "properties": dict(relationship)
                    })
                
                return {
                    "nodes": list(nodes.values()),
                    "edges": edges
                }
        
        except Exception as e:
            logger.error(f"Error getting entity graph: {e}")
            return {"nodes": [], "edges": []}
    
    async def get_entity_connections(
        self,
        entity_id: str,
        connection_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Получить связи сущности
        
        Args:
            entity_id: ID сущности
            connection_type: Фильтр по типу связи
        
        Returns:
            Список связанных сущностей
        """
        if self.driver is None:
            return []
        
        try:
            with self._get_session() as session:
                query = """
                MATCH (start {id: $entity_id})-[r:RELATES_TO]-(connected)
                """
                
                if connection_type:
                    query += " WHERE r.type = $connection_type"
                
                query += """
                RETURN connected, r.type as relation_type, COALESCE(r.weight, 1.0) as weight
                ORDER BY weight DESC
                LIMIT 50
                """
                
                params = {"entity_id": entity_id}
                if connection_type:
                    params["connection_type"] = connection_type
                
                result = session.run(query, **params)
                
                connections = []
                for record in result:
                    node = record["connected"]
                    connections.append({
                        "id": node.id,
                        "type": list(node.labels)[0] if node.labels else "Unknown",
                        "title": node.get("name", node.id),
                        "relation_type": record["relation_type"],
                        "score": record.get("weight", 1.0)
                    })
                
                return connections
        
        except Exception as e:
            logger.error(f"Error getting connections: {e}")
            return []
    
    async def delete_project(self, project_id: str):
        """Удаление всех узлов и связей проекта"""
        if self.driver is None:
            return
        
        try:
            with self._get_session() as session:
                # Удаление всех связей проекта
                query1 = """
                MATCH ()-[r {project_id: $project_id}]-()
                DELETE r
                """
                session.run(query1, project_id=project_id)
                
                # Удаление всех узлов проекта
                query2 = """
                MATCH (n {project_id: $project_id})
                DELETE n
                """
                session.run(query2, project_id=project_id)
                
                logger.info(f"Deleted project {project_id} from graph")
        
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
    
    def close(self):
        """Закрытие соединения"""
        if self.driver:
            self.driver.close()

