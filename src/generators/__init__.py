from src.generators.factory import ExerciseFactory
from src.generators.math_generator import MathGenerator
from src.generators.course_generator import CourseGenerator
from src.generators.problem_generator import ProblemGenerator
from src.generators.divisibility_generator import DivisibilityGenerator

# Register generators
ExerciseFactory.register("calcul", MathGenerator())
ExerciseFactory.register("cours", CourseGenerator())
ExerciseFactory.register("probleme", ProblemGenerator())
ExerciseFactory.register("divisibilite", DivisibilityGenerator())
