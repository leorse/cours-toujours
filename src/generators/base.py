from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ExerciseGenerator(ABC):
    """
    Abstract base class for all exercise generators.
    """
    
    @abstractmethod
    def generate(self, config: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        """
        Generate a list of exercises based on the configuration.
        
        Args:
            config: A dictionary containing generator-specific configuration (e.g., 'focus', 'difficulty').
            count: The number of exercises to generate.
            
        Returns:
            A list of exercise dictionaries. Each dictionary must have at least:
            - id: Unique identifier
            - type: The type of exercise generic (e.g., 'input', 'qcm')
            - question: The question text
            - answer: The expected answer
            - tag: The hierarchical tag (e.g., 'math:calcul:addition')
            - meta: (Optional) Visual blueprints or other metadata
        """
        pass
