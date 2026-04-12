package fr.parcours.service;

import fr.parcours.model.content.RoadStep;
import fr.parcours.model.dto.GeneratedExercise;
import fr.parcours.model.dto.StepResult;
import fr.parcours.model.dto.SubmitRequest;
import fr.parcours.model.entity.RoadStepProgress;
import fr.parcours.model.entity.SubjectProgress;
import fr.parcours.model.entity.User;
import fr.parcours.repository.ExerciseLogRepository;
import fr.parcours.repository.RoadStepProgressRepository;
import fr.parcours.repository.SubjectProgressRepository;
import fr.parcours.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
@DisplayName("ProgressService")
class ProgressServiceTest {

    @Mock RoadStepProgressRepository stepRepo;
    @Mock SubjectProgressRepository subjectRepo;
    @Mock ExerciseLogRepository logRepo;
    @Mock UserRepository userRepo;
    @Mock SmartCompareService smartCompare;
    @Mock ContentManagerService contentManager;

    @InjectMocks
    ProgressService service;

    private static final String USER_ID = "user-1";
    private static final String STEP_ID = "maths.intro";
    private static final String SUBJECT_ID = "maths";

    private RoadStep makeStep(String type) {
        RoadStep step = new RoadStep();
        step.setId(STEP_ID);
        step.setSubjectId(SUBJECT_ID);
        step.setType(type);
        return step;
    }

    private GeneratedExercise makeExercise(String id, String answer, List<String> tags) {
        GeneratedExercise ex = new GeneratedExercise();
        ex.setId(id);
        ex.setAnswer(answer);
        ex.setTags(tags);
        return ex;
    }

    @BeforeEach
    void setupCommonMocks() {
        // Par défaut : pas de progression existante
        when(stepRepo.findByUserIdAndStepId(anyString(), anyString())).thenReturn(Optional.empty());
        when(stepRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

        // Utilisateur avec 0 XP
        User user = User.builder().id(USER_ID).username("test").totalXp(0).build();
        when(userRepo.findById(USER_ID)).thenReturn(Optional.of(user));
        when(userRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

        // SubjectProgress vide
        when(subjectRepo.findByUserIdAndSubjectId(anyString(), anyString())).thenReturn(Optional.empty());
        when(subjectRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));
    }

    // ── completeTheoryStep ────────────────────────────────────────────────────

    @Nested
    @DisplayName("completeTheoryStep")
    class Theory {

        @BeforeEach
        void setup() {
            when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("cours")));
        }

        @Test
        @DisplayName("retourne success=true")
        void returnsSuccess() {
            StepResult r = service.completeTheoryStep(USER_ID, STEP_ID);
            assertThat(r.isSuccess()).isTrue();
        }

        @Test
        @DisplayName("retourne xpEarned=20")
        void returns20Xp() {
            StepResult r = service.completeTheoryStep(USER_ID, STEP_ID);
            assertThat(r.getXpEarned()).isEqualTo(20);
        }

        @Test
        @DisplayName("sauvegarde l'étape comme complétée")
        void savesCompleted() {
            service.completeTheoryStep(USER_ID, STEP_ID);

            ArgumentCaptor<RoadStepProgress> cap = ArgumentCaptor.forClass(RoadStepProgress.class);
            verify(stepRepo).save(cap.capture());
            assertThat(cap.getValue().isCompleted()).isTrue();
        }

        @Test
        @DisplayName("incrémente le XP de l'utilisateur")
        void incrementsUserXp() {
            service.completeTheoryStep(USER_ID, STEP_ID);

            ArgumentCaptor<User> cap = ArgumentCaptor.forClass(User.class);
            verify(userRepo).save(cap.capture());
            assertThat(cap.getValue().getTotalXp()).isEqualTo(20);
        }

        @Test
        @DisplayName("crée SubjectProgress si inexistant")
        void createsSubjectProgress() {
            service.completeTheoryStep(USER_ID, STEP_ID);

            ArgumentCaptor<SubjectProgress> cap = ArgumentCaptor.forClass(SubjectProgress.class);
            verify(subjectRepo).save(cap.capture());
            assertThat(cap.getValue().getScore()).isEqualTo(20);
            assertThat(cap.getValue().getSubjectId()).isEqualTo(SUBJECT_ID);
        }
    }

    // ── evaluateExercises — succès ────────────────────────────────────────────

    @Nested
    @DisplayName("evaluateExercises — succès (≥ 50%)")
    class EvaluationSuccess {

        @BeforeEach
        void setup() {
            when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("practice")));
        }

        private SubmitRequest makeRequest(int totalExercises, int correctCount) {
            List<GeneratedExercise> exos = new java.util.ArrayList<>();
            Map<String, Object> answers = new java.util.HashMap<>();
            for (int i = 0; i < totalExercises; i++) {
                String id = "ex-" + i;
                exos.add(makeExercise(id, "42", List.of("math.calcul")));
                answers.put(id, i < correctCount ? "42" : "wrong");
            }
            // SmartCompare doit retourner true pour les bonnes réponses
            when(smartCompare.compare(eq("42"), eq("42"))).thenReturn(true);
            when(smartCompare.compare(eq("wrong"), eq("42"))).thenReturn(false);

            SubmitRequest req = new SubmitRequest();
            req.setStepId(STEP_ID);
            req.setGeneratedExercises(exos);
            req.setAnswers(answers);
            return req;
        }

        @Test
        @DisplayName("4/4 corrects → success=true, xpEarned=40")
        void allCorrect() {
            StepResult r = service.evaluateExercises(USER_ID, makeRequest(4, 4));
            assertThat(r.isSuccess()).isTrue();
            assertThat(r.getCorrectCount()).isEqualTo(4);
            assertThat(r.getTotalCount()).isEqualTo(4);
            assertThat(r.getXpEarned()).isEqualTo(40);
        }

        @Test
        @DisplayName("3/4 corrects → success=true (75% ≥ 50%)")
        void threeOfFour() {
            StepResult r = service.evaluateExercises(USER_ID, makeRequest(4, 3));
            assertThat(r.isSuccess()).isTrue();
            assertThat(r.getCorrectCount()).isEqualTo(3);
            assertThat(r.getXpEarned()).isEqualTo(30);
        }

        @Test
        @DisplayName("2/4 corrects → success=true (50% = seuil)")
        void exactlyHalf() {
            StepResult r = service.evaluateExercises(USER_ID, makeRequest(4, 2));
            assertThat(r.isSuccess()).isTrue();
        }

        @Test
        @DisplayName("scorePercent est correctement calculé")
        void scorePercent() {
            StepResult r = service.evaluateExercises(USER_ID, makeRequest(4, 3));
            assertThat(r.getScorePercent()).isEqualTo(75.0);
        }

        @Test
        @DisplayName("answerResults contient un booléen par exercice")
        void answerResultsPopulated() {
            StepResult r = service.evaluateExercises(USER_ID, makeRequest(4, 3));
            assertThat(r.getAnswerResults()).hasSize(4);
        }

        @Test
        @DisplayName("étape marquée complétée en cas de succès")
        void stepMarkedCompleted() {
            service.evaluateExercises(USER_ID, makeRequest(2, 2));
            ArgumentCaptor<RoadStepProgress> cap = ArgumentCaptor.forClass(RoadStepProgress.class);
            verify(stepRepo).save(cap.capture());
            assertThat(cap.getValue().isCompleted()).isTrue();
        }
    }

    // ── evaluateExercises — échec ─────────────────────────────────────────────

    @Nested
    @DisplayName("evaluateExercises — échec (< 50%)")
    class EvaluationFailure {

        @BeforeEach
        void setup() {
            when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("practice")));
        }

        @Test
        @DisplayName("1/4 corrects → success=false")
        void oneOfFour() {
            List<GeneratedExercise> exos = List.of(
                makeExercise("e1", "42", List.of("math")),
                makeExercise("e2", "42", List.of("math")),
                makeExercise("e3", "42", List.of("math")),
                makeExercise("e4", "42", List.of("math"))
            );
            when(smartCompare.compare(eq("42"), eq("42"))).thenReturn(true);
            when(smartCompare.compare(eq("x"), eq("42"))).thenReturn(false);

            SubmitRequest req = new SubmitRequest();
            req.setStepId(STEP_ID);
            req.setGeneratedExercises(exos);
            req.setAnswers(Map.of("e1", "42", "e2", "x", "e3", "x", "e4", "x"));

            StepResult r = service.evaluateExercises(USER_ID, req);
            assertThat(r.isSuccess()).isFalse();
            assertThat(r.getXpEarned()).isEqualTo(0);
        }
    }

    // ── Mastery (type=validation) ─────────────────────────────────────────────

    @Nested
    @DisplayName("Mastery — type=validation")
    class Mastery {

        @Test
        @DisplayName("score parfait → mastery +1 (plafonné à 3)")
        void perfectScoreIncreasesMastery() {
            when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("validation")));
            RoadStepProgress existing = RoadStepProgress.builder()
                .id("p1").userId(USER_ID).stepId(STEP_ID).mastery(1).build();
            when(stepRepo.findByUserIdAndStepId(USER_ID, STEP_ID)).thenReturn(Optional.of(existing));

            GeneratedExercise ex = makeExercise("e1", "42", List.of("math"));
            when(smartCompare.compare("42", "42")).thenReturn(true);

            SubmitRequest req = new SubmitRequest();
            req.setStepId(STEP_ID);
            req.setGeneratedExercises(List.of(ex));
            req.setAnswers(Map.of("e1", "42"));

            service.evaluateExercises(USER_ID, req);

            ArgumentCaptor<RoadStepProgress> cap = ArgumentCaptor.forClass(RoadStepProgress.class);
            verify(stepRepo).save(cap.capture());
            assertThat(cap.getValue().getMastery()).isEqualTo(2);
        }

        @Test
        @DisplayName("score imparfait → mastery -1 (plancher à 0)")
        void imperfectScoreDecreasesMastery() {
            when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("validation")));
            RoadStepProgress existing = RoadStepProgress.builder()
                .id("p1").userId(USER_ID).stepId(STEP_ID).mastery(2).build();
            when(stepRepo.findByUserIdAndStepId(USER_ID, STEP_ID)).thenReturn(Optional.of(existing));

            GeneratedExercise e1 = makeExercise("e1", "42", List.of("math"));
            GeneratedExercise e2 = makeExercise("e2", "42", List.of("math"));
            when(smartCompare.compare("42", "42")).thenReturn(true);
            when(smartCompare.compare("x", "42")).thenReturn(false);

            SubmitRequest req = new SubmitRequest();
            req.setStepId(STEP_ID);
            req.setGeneratedExercises(List.of(e1, e2));
            req.setAnswers(Map.of("e1", "42", "e2", "x"));

            service.evaluateExercises(USER_ID, req);

            ArgumentCaptor<RoadStepProgress> cap = ArgumentCaptor.forClass(RoadStepProgress.class);
            verify(stepRepo).save(cap.capture());
            assertThat(cap.getValue().getMastery()).isEqualTo(1);
        }

        @Test
        @DisplayName("mastery déjà à 3 + score parfait → reste à 3")
        void masteryCapAt3() {
            when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("validation")));
            RoadStepProgress existing = RoadStepProgress.builder()
                .id("p1").userId(USER_ID).stepId(STEP_ID).mastery(3).build();
            when(stepRepo.findByUserIdAndStepId(USER_ID, STEP_ID)).thenReturn(Optional.of(existing));

            GeneratedExercise ex = makeExercise("e1", "42", List.of("math"));
            when(smartCompare.compare("42", "42")).thenReturn(true);

            SubmitRequest req = new SubmitRequest();
            req.setStepId(STEP_ID);
            req.setGeneratedExercises(List.of(ex));
            req.setAnswers(Map.of("e1", "42"));

            service.evaluateExercises(USER_ID, req);

            ArgumentCaptor<RoadStepProgress> cap = ArgumentCaptor.forClass(RoadStepProgress.class);
            verify(stepRepo).save(cap.capture());
            assertThat(cap.getValue().getMastery()).isEqualTo(3);
        }

        @Test
        @DisplayName("mastery à 0 + score imparfait → reste à 0")
        void masteryFloorAt0() {
            when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("validation")));
            RoadStepProgress existing = RoadStepProgress.builder()
                .id("p1").userId(USER_ID).stepId(STEP_ID).mastery(0).build();
            when(stepRepo.findByUserIdAndStepId(USER_ID, STEP_ID)).thenReturn(Optional.of(existing));

            GeneratedExercise ex = makeExercise("e1", "42", List.of("math"));
            when(smartCompare.compare("x", "42")).thenReturn(false);

            SubmitRequest req = new SubmitRequest();
            req.setStepId(STEP_ID);
            req.setGeneratedExercises(List.of(ex));
            req.setAnswers(Map.of("e1", "x"));

            service.evaluateExercises(USER_ID, req);

            ArgumentCaptor<RoadStepProgress> cap = ArgumentCaptor.forClass(RoadStepProgress.class);
            verify(stepRepo).save(cap.capture());
            assertThat(cap.getValue().getMastery()).isEqualTo(0);
        }

        @Test
        @DisplayName("type=practice → mastery inchangé")
        void practiceTypeNoMasteryChange() {
            when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("practice")));
            RoadStepProgress existing = RoadStepProgress.builder()
                .id("p1").userId(USER_ID).stepId(STEP_ID).mastery(2).build();
            when(stepRepo.findByUserIdAndStepId(USER_ID, STEP_ID)).thenReturn(Optional.of(existing));

            GeneratedExercise ex = makeExercise("e1", "42", List.of("math"));
            when(smartCompare.compare("42", "42")).thenReturn(true);

            SubmitRequest req = new SubmitRequest();
            req.setStepId(STEP_ID);
            req.setGeneratedExercises(List.of(ex));
            req.setAnswers(Map.of("e1", "42"));

            service.evaluateExercises(USER_ID, req);

            ArgumentCaptor<RoadStepProgress> cap = ArgumentCaptor.forClass(RoadStepProgress.class);
            verify(stepRepo).save(cap.capture());
            assertThat(cap.getValue().getMastery()).isEqualTo(2);
        }
    }

    // ── Logs exercices ────────────────────────────────────────────────────────

    @Test
    @DisplayName("un ExerciseLog est sauvegardé par tag par exercice")
    void logsAreCreatedPerTag() {
        when(contentManager.getStep(STEP_ID)).thenReturn(Optional.of(makeStep("practice")));
        GeneratedExercise ex = makeExercise("e1", "42", List.of("math.calcul.mul", "math.calcul"));
        when(smartCompare.compare(any(), any())).thenReturn(true);

        SubmitRequest req = new SubmitRequest();
        req.setStepId(STEP_ID);
        req.setGeneratedExercises(List.of(ex));
        req.setAnswers(Map.of("e1", "42"));

        service.evaluateExercises(USER_ID, req);

        // 2 tags → 2 logs
        verify(logRepo, times(2)).save(any());
    }
}
