package fr.parcours.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import fr.parcours.model.content.RoadStep;
import fr.parcours.model.dto.GeneratedExercise;
import fr.parcours.model.dto.StepResult;
import fr.parcours.model.dto.SubmitRequest;
import fr.parcours.service.ContentManagerService;
import fr.parcours.service.ProgressService;
import fr.parcours.config.SecurityConfig;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(SubmitController.class)
@Import(SecurityConfig.class)
@DisplayName("SubmitController")
class SubmitControllerTest {

    @Autowired MockMvc mvc;
    @Autowired ObjectMapper json;
    @MockBean ProgressService progressService;
    @MockBean ContentManagerService contentManager;

    private MockHttpSession sessionWith(String userId) {
        MockHttpSession s = new MockHttpSession();
        s.setAttribute("userId", userId);
        return s;
    }

    private RoadStep makeStep(String id, String type, String subjectId) {
        RoadStep step = new RoadStep();
        step.setId(id);
        step.setType(type);
        step.setSubjectId(subjectId);
        return step;
    }

    private StepResult successResult(int xp) {
        StepResult r = new StepResult();
        r.setSuccess(true);
        r.setXpEarned(xp);
        r.setCorrectCount(1);
        r.setTotalCount(1);
        r.setScorePercent(100.0);
        r.setMessage("Bravo !");
        r.setAnswerResults(Map.of());
        return r;
    }

    // ── Sans session ──────────────────────────────────────────────────────────

    @Test
    @DisplayName("POST /api/submit sans session → 401")
    void noSession() throws Exception {
        SubmitRequest req = new SubmitRequest();
        req.setStepId("maths.intro");

        mvc.perform(post("/api/submit")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsString(req)))
            .andExpect(status().isUnauthorized());
    }

    // ── Étape introuvable ─────────────────────────────────────────────────────

    @Test
    @DisplayName("stepId inconnu → 404")
    void unknownStep() throws Exception {
        when(contentManager.getStep("unknown.step")).thenReturn(Optional.empty());

        SubmitRequest req = new SubmitRequest();
        req.setStepId("unknown.step");

        mvc.perform(post("/api/submit")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsString(req))
                .session(sessionWith("u1")))
            .andExpect(status().isNotFound());
    }

    // ── Étape de type cours ───────────────────────────────────────────────────

    @Nested
    @DisplayName("Type cours/theory")
    class Theory {

        @Test
        @DisplayName("type=cours → appelle completeTheoryStep, retourne 200")
        void coursType() throws Exception {
            when(contentManager.getStep("maths.intro")).thenReturn(
                Optional.of(makeStep("maths.intro", "cours", "maths")));
            when(progressService.completeTheoryStep("u1", "maths.intro"))
                .thenReturn(successResult(20));

            SubmitRequest req = new SubmitRequest();
            req.setStepId("maths.intro");

            mvc.perform(post("/api/submit")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(req))
                    .session(sessionWith("u1")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.xpEarned").value(20));

            verify(progressService).completeTheoryStep("u1", "maths.intro");
        }

        @Test
        @DisplayName("type=theory → appelle completeTheoryStep")
        void theoryType() throws Exception {
            when(contentManager.getStep("maths.theory")).thenReturn(
                Optional.of(makeStep("maths.theory", "theory", "maths")));
            when(progressService.completeTheoryStep("u1", "maths.theory"))
                .thenReturn(successResult(20));

            SubmitRequest req = new SubmitRequest();
            req.setStepId("maths.theory");

            mvc.perform(post("/api/submit")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(req))
                    .session(sessionWith("u1")))
                .andExpect(status().isOk());

            verify(progressService).completeTheoryStep("u1", "maths.theory");
        }
    }

    // ── Étape d'exercices ─────────────────────────────────────────────────────

    @Nested
    @DisplayName("Type practice/exam/validation")
    class Exercises {

        @Test
        @DisplayName("type=practice → appelle evaluateExercises, retourne résultat")
        void practiceType() throws Exception {
            when(contentManager.getStep("maths.practice")).thenReturn(
                Optional.of(makeStep("maths.practice", "practice", "maths")));

            StepResult result = new StepResult();
            result.setSuccess(true);
            result.setCorrectCount(3);
            result.setTotalCount(4);
            result.setScorePercent(75.0);
            result.setXpEarned(30);
            result.setMessage("Bravo ! 3/4");
            result.setAnswerResults(Map.of("e1", true, "e2", true, "e3", true, "e4", false));

            when(progressService.evaluateExercises(eq("u1"), any())).thenReturn(result);

            GeneratedExercise ex = new GeneratedExercise();
            ex.setId("e1"); ex.setAnswer("42");

            SubmitRequest req = new SubmitRequest();
            req.setStepId("maths.practice");
            req.setGeneratedExercises(List.of(ex));
            req.setAnswers(Map.of("e1", "42"));

            mvc.perform(post("/api/submit")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(req))
                    .session(sessionWith("u1")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.correctCount").value(3))
                .andExpect(jsonPath("$.totalCount").value(4))
                .andExpect(jsonPath("$.scorePercent").value(75.0))
                .andExpect(jsonPath("$.xpEarned").value(30));

            verify(progressService).evaluateExercises(eq("u1"), any());
        }

        @Test
        @DisplayName("type=validation → appelle evaluateExercises")
        void validationType() throws Exception {
            when(contentManager.getStep("maths.valid")).thenReturn(
                Optional.of(makeStep("maths.valid", "validation", "maths")));
            when(progressService.evaluateExercises(eq("u1"), any())).thenReturn(successResult(10));

            SubmitRequest req = new SubmitRequest();
            req.setStepId("maths.valid");
            req.setGeneratedExercises(List.of());
            req.setAnswers(Map.of());

            mvc.perform(post("/api/submit")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(req))
                    .session(sessionWith("u1")))
                .andExpect(status().isOk());

            verify(progressService).evaluateExercises(eq("u1"), any());
        }

        @Test
        @DisplayName("échec (success=false) → toujours 200 (pas d'erreur HTTP)")
        void failureStillReturns200() throws Exception {
            when(contentManager.getStep("maths.practice")).thenReturn(
                Optional.of(makeStep("maths.practice", "practice", "maths")));

            StepResult fail = new StepResult();
            fail.setSuccess(false);
            fail.setCorrectCount(1);
            fail.setTotalCount(4);
            fail.setScorePercent(25.0);
            fail.setXpEarned(0);
            fail.setMessage("Essaie encore !");
            fail.setAnswerResults(Map.of());
            when(progressService.evaluateExercises(eq("u1"), any())).thenReturn(fail);

            SubmitRequest req = new SubmitRequest();
            req.setStepId("maths.practice");
            req.setGeneratedExercises(List.of());
            req.setAnswers(Map.of());

            mvc.perform(post("/api/submit")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(req))
                    .session(sessionWith("u1")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.xpEarned").value(0));
        }
    }
}
