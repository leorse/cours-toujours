package fr.parcours.service;

import fr.parcours.model.content.ExerciseTemplate;
import fr.parcours.model.dto.GeneratedExercise;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("ExerciseEngineService")
class ExerciseEngineServiceTest {

    private ExerciseEngineService engine;

    @BeforeEach
    void setUp() {
        engine = new ExerciseEngineService();
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private ExerciseTemplate template(String id, Map<String, Object> vars,
                                      Map<String, Object> content, String logic) {
        ExerciseTemplate t = new ExerciseTemplate();
        t.setId(id);
        t.setTags(List.of("test"));
        t.setVars(vars);
        t.setContent(content);
        t.setLogic(logic);
        t.setInteraction("input");
        return t;
    }

    // ── Génération de base ────────────────────────────────────────────────────

    @Nested
    @DisplayName("Génération d'exercice")
    class Generation {

        @Test
        @DisplayName("retourne un Optional non vide pour un template valide")
        void validTemplateProducesExercise() {
            ExerciseTemplate t = template("t1",
                Map.of("a", Map.of("min", 1, "max", 10),
                       "b", Map.of("min", 1, "max", 10)),
                Map.of("question", "Combien font {a} x {b} ?"),
                "{a} * {b}");

            Optional<GeneratedExercise> result = engine.generateExercise(t);
            assertThat(result).isPresent();
        }

        @Test
        @DisplayName("l'id de l'exercice généré n'est pas null")
        void exerciseHasId() {
            ExerciseTemplate t = template("t1", null,
                Map.of("question", "Question ?", "answer", "42"), null);
            assertThat(engine.generateExercise(t)).isPresent()
                .get().extracting(GeneratedExercise::getId).isNotNull();
        }

        @Test
        @DisplayName("templateId est copié dans l'exercice généré")
        void templateIdCopied() {
            ExerciseTemplate t = template("mon_template", null,
                Map.of("question", "Q", "answer", "R"), null);
            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getTemplateId()).isEqualTo("mon_template");
        }

        @Test
        @DisplayName("tags sont copiés dans l'exercice généré")
        void tagsCopied() {
            ExerciseTemplate t = template("t1", null,
                Map.of("question", "Q"), null);
            t.setTags(List.of("math.calcul.mul", "math.calcul"));
            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat((List<String>) ex.getTags()).containsExactly("math.calcul.mul", "math.calcul");
        }
    }

    // ── Variables ─────────────────────────────────────────────────────────────

    @Nested
    @DisplayName("Génération de variables")
    class Variables {

        @RepeatedTest(20)
        @DisplayName("variable range — valeur dans [min, max]")
        void rangeVariable() {
            ExerciseTemplate t = template("t1",
                Map.of("a", Map.of("min", 3, "max", 7)),
                Map.of("question", "{a}"), "{a}");

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            int a = Integer.parseInt(ex.getAnswer().toString());
            assertThat(a).isBetween(3, 7);
        }

        @RepeatedTest(10)
        @DisplayName("variable liste — valeur dans la liste")
        void listVariable() {
            ExerciseTemplate t = template("t1",
                Map.of("fruit", List.of("pomme", "poire", "cerise")),
                Map.of("question", "Un {fruit} ?", "answer", "{fruit}"), null);

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getAnswer().toString())
                .isIn("pomme", "poire", "cerise");
        }

        @Test
        @DisplayName("variable statique — valeur fixe")
        void staticVariable() {
            ExerciseTemplate t = template("t1",
                Map.of("unit", "cm"),
                Map.of("question", "Unité : {unit}", "answer", "{unit}"), null);

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getAnswer().toString()).isEqualTo("cm");
        }

        @Test
        @DisplayName("variables null → pas d'erreur, variables vides")
        void nullVars() {
            ExerciseTemplate t = template("t1", null,
                Map.of("question", "Q fixe", "answer", "R"), null);

            assertThat(engine.generateExercise(t)).isPresent();
        }
    }

    // ── Interpolation ─────────────────────────────────────────────────────────

    @Nested
    @DisplayName("Interpolation")
    class Interpolation {

        @Test
        @DisplayName("{var} remplacé dans la question")
        void varInQuestion() {
            ExerciseTemplate t = template("t1",
                Map.of("a", 5),
                Map.of("question", "La valeur est {a}"), "{a}");

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getQuestion()).isEqualTo("La valeur est 5");
        }

        @Test
        @DisplayName("[[expr]] évalué dans la question")
        void exprInQuestion() {
            ExerciseTemplate t = template("t1",
                Map.of("a", 4, "b", 3),
                Map.of("question", "[[{a} + {b}]] = ?"), "{a} + {b}");

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getQuestion()).isEqualTo("7 = ?");
        }

        @Test
        @DisplayName("{var} remplacé dans les options")
        void varInOptions() {
            ExerciseTemplate t = template("t1",
                Map.of("a", 3, "b", 4),
                Map.of("question", "Q",
                       "options", List.of("{a}", "{b}", "10")), null);

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getOptions()).containsExactly("3", "4", "10");
        }

        @Test
        @DisplayName("{var} remplacé dans l'explication")
        void varInExplanation() {
            ExerciseTemplate t = template("t1",
                Map.of("a", 6, "b", 7),
                Map.of("question", "Q",
                       "explanation", "{a} x {b} = [[{a} * {b}]]"), null);
            t.setLogic("{a} * {b}");

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getExplanation()).isEqualTo("6 x 7 = 42");
        }
    }

    // ── Calcul de la réponse ──────────────────────────────────────────────────

    @Nested
    @DisplayName("Calcul de la réponse")
    class Reponse {

        @Test
        @DisplayName("logic: addition → réponse correcte")
        void logicAddition() {
            ExerciseTemplate t = template("t1",
                Map.of("a", 8, "b", 5),
                Map.of("question", "{a} + {b} = ?"), "{a} + {b}");

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getAnswer().toString()).isEqualTo("13");
        }

        @Test
        @DisplayName("logic: multiplication → réponse correcte")
        void logicMultiplication() {
            ExerciseTemplate t = template("t1",
                Map.of("a", 7, "b", 6),
                Map.of("question", "{a} x {b} = ?"), "{a} * {b}");

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getAnswer().toString()).isEqualTo("42");
        }

        @Test
        @DisplayName("logic: soustraction → réponse correcte")
        void logicSoustraction() {
            ExerciseTemplate t = template("t1",
                Map.of("a", 10, "b", 3),
                Map.of("question", "{a} - {b} = ?"), "{a} - {b}");

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getAnswer().toString()).isEqualTo("7");
        }

        @Test
        @DisplayName("logic: division entière → réponse correcte")
        void logicDivision() {
            ExerciseTemplate t = template("t1",
                Map.of("a", 12, "b", 4),
                Map.of("question", "{a} / {b} = ?"), "{a} / {b}");

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getAnswer().toString()).isEqualTo("3");
        }

        @Test
        @DisplayName("sans logic: réponse statique du content")
        void staticAnswer() {
            ExerciseTemplate t = template("t1", null,
                Map.of("question", "Capitale de la France ?", "answer", "Paris"), null);

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getAnswer().toString()).isEqualTo("Paris");
        }

        @Test
        @DisplayName("sans logic: réponse liste → liste retournée")
        void listAnswer() {
            ExerciseTemplate t = template("t1", null,
                Map.of("question", "Q", "options", List.of("A", "B", "C"),
                       "answer", List.of("A", "C")), null);

            GeneratedExercise ex = engine.generateExercise(t).orElseThrow();
            assertThat(ex.getAnswer()).isInstanceOf(List.class);
            @SuppressWarnings("unchecked")
            List<String> answerList = (List<String>) ex.getAnswer();
            assertThat(answerList).containsExactly("A", "C");
        }
    }

    // ── generateExercises ─────────────────────────────────────────────────────

    @Nested
    @DisplayName("generateExercises(templates, count)")
    class Batch {

        @Test
        @DisplayName("liste vide → liste vide")
        void emptyTemplates() {
            assertThat(engine.generateExercises(List.of(), 10)).isEmpty();
        }

        @Test
        @DisplayName("count=5 avec un template valide → 5 exercices")
        void correctCount() {
            ExerciseTemplate t = template("t1",
                Map.of("a", Map.of("min", 1, "max", 100)),
                Map.of("question", "{a} ?"), "{a}");

            List<GeneratedExercise> result = engine.generateExercises(List.of(t), 5);
            assertThat(result).hasSize(5);
        }

        @Test
        @DisplayName("tous les exercices ont un id unique")
        void uniqueIds() {
            ExerciseTemplate t = template("t1",
                Map.of("a", Map.of("min", 1, "max", 1000)),
                Map.of("question", "{a} ?"), "{a}");

            List<GeneratedExercise> result = engine.generateExercises(List.of(t), 10);
            long distinctIds = result.stream().map(GeneratedExercise::getId).distinct().count();
            assertThat(distinctIds).isEqualTo(result.size());
        }
    }
}
