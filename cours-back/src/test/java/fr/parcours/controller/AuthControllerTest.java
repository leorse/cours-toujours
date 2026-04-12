package fr.parcours.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import fr.parcours.model.entity.User;
import fr.parcours.repository.UserRepository;
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

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(AuthController.class)
@Import(SecurityConfig.class)
@DisplayName("AuthController")
class AuthControllerTest {

    @Autowired MockMvc mvc;
    @Autowired ObjectMapper json;
    @MockBean UserRepository userRepo;

    private User sampleUser() {
        return User.builder().id("u1").username("alice").avatar("").totalXp(50).build();
    }

    // ── GET /api/auth/users ───────────────────────────────────────────────────

    @Nested
    @DisplayName("GET /api/auth/users")
    class ListUsers {

        @Test
        @DisplayName("retourne la liste des utilisateurs")
        void returnsList() throws Exception {
            when(userRepo.findAll()).thenReturn(List.of(sampleUser()));

            mvc.perform(get("/api/auth/users"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].username").value("alice"))
                .andExpect(jsonPath("$[0].totalXp").value(50));
        }

        @Test
        @DisplayName("retourne une liste vide si aucun utilisateur")
        void returnsEmpty() throws Exception {
            when(userRepo.findAll()).thenReturn(List.of());

            mvc.perform(get("/api/auth/users"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
        }
    }

    // ── POST /api/auth/users ──────────────────────────────────────────────────

    @Nested
    @DisplayName("POST /api/auth/users — création de compte")
    class CreateUser {

        @Test
        @DisplayName("crée l'utilisateur et retourne 200 avec le DTO")
        void createsUser() throws Exception {
            when(userRepo.existsByUsername("bob")).thenReturn(false);
            when(userRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

            mvc.perform(post("/api/auth/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(Map.of("username", "bob"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("bob"))
                .andExpect(jsonPath("$.id").isNotEmpty());
        }

        @Test
        @DisplayName("username vide → 400")
        void emptyUsername() throws Exception {
            mvc.perform(post("/api/auth/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(Map.of("username", ""))))
                .andExpect(status().isBadRequest());
        }

        @Test
        @DisplayName("username existant → 409")
        void duplicateUsername() throws Exception {
            when(userRepo.existsByUsername("alice")).thenReturn(true);

            mvc.perform(post("/api/auth/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(Map.of("username", "alice"))))
                .andExpect(status().isConflict());
        }

        @Test
        @DisplayName("la création ouvre la session (userId dans session)")
        void setsSession() throws Exception {
            when(userRepo.existsByUsername("carol")).thenReturn(false);
            when(userRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

            var result = mvc.perform(post("/api/auth/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(Map.of("username", "carol"))))
                .andExpect(status().isOk())
                .andReturn();

            MockHttpSession session = (MockHttpSession) result.getRequest().getSession(false);
            assertThat(session).isNotNull();
            assertThat(session.getAttribute("userId")).isNotNull().isInstanceOf(String.class);
        }
    }

    // ── POST /api/auth/login ──────────────────────────────────────────────────

    @Nested
    @DisplayName("POST /api/auth/login")
    class Login {

        @Test
        @DisplayName("userId valide → 200 avec le DTO utilisateur")
        void validLogin() throws Exception {
            when(userRepo.findById("u1")).thenReturn(Optional.of(sampleUser()));

            mvc.perform(post("/api/auth/login")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(Map.of("userId", "u1"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("alice"));
        }

        @Test
        @DisplayName("userId inconnu → 404")
        void unknownUser() throws Exception {
            when(userRepo.findById("unknown")).thenReturn(Optional.empty());

            mvc.perform(post("/api/auth/login")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(Map.of("userId", "unknown"))))
                .andExpect(status().isNotFound());
        }

        @Test
        @DisplayName("login valide ouvre la session")
        void setsSession() throws Exception {
            when(userRepo.findById("u1")).thenReturn(Optional.of(sampleUser()));

            var result = mvc.perform(post("/api/auth/login")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(Map.of("userId", "u1"))))
                .andReturn();

            MockHttpSession session = (MockHttpSession) result.getRequest().getSession(false);
            assertThat(session).isNotNull();
            assertThat(session.getAttribute("userId")).isEqualTo("u1");
        }
    }

    // ── GET /api/auth/me ──────────────────────────────────────────────────────

    @Nested
    @DisplayName("GET /api/auth/me")
    class Me {

        @Test
        @DisplayName("session valide → 200 avec le DTO")
        void authenticated() throws Exception {
            when(userRepo.findById("u1")).thenReturn(Optional.of(sampleUser()));
            MockHttpSession session = new MockHttpSession();
            session.setAttribute("userId", "u1");

            mvc.perform(get("/api/auth/me").session(session))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("alice"));
        }

        @Test
        @DisplayName("sans session → 401")
        void unauthenticated() throws Exception {
            mvc.perform(get("/api/auth/me"))
                .andExpect(status().isUnauthorized());
        }
    }

    // ── POST /api/auth/logout ─────────────────────────────────────────────────

    @Test
    @DisplayName("POST /api/auth/logout → 200, session invalidée")
    void logout() throws Exception {
        MockHttpSession session = new MockHttpSession();
        session.setAttribute("userId", "u1");

        mvc.perform(post("/api/auth/logout").session(session))
            .andExpect(status().isOk());

        assertThat(session.isInvalid()).isTrue();
    }
}
