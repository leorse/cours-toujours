package fr.parcours.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("SmartCompareService")
class SmartCompareServiceTest {

    private SmartCompareService service;

    @BeforeEach
    void setUp() {
        service = new SmartCompareService();
    }

    // ── Cas nuls ─────────────────────────────────────────────────────────────

    @Test
    @DisplayName("null user → false")
    void nullUser() {
        assertThat(service.compare(null, "42")).isFalse();
    }

    @Test
    @DisplayName("null expected → false")
    void nullExpected() {
        assertThat(service.compare("42", null)).isFalse();
    }

    @Test
    @DisplayName("les deux null → false")
    void bothNull() {
        assertThat(service.compare(null, null)).isFalse();
    }

    // ── Comparaison string ────────────────────────────────────────────────────

    @Nested
    @DisplayName("Strings")
    class Strings {

        @Test
        @DisplayName("identiques → true")
        void same() {
            assertThat(service.compare("pomme", "pomme")).isTrue();
        }

        @Test
        @DisplayName("insensible à la casse → true")
        void caseInsensitive() {
            assertThat(service.compare("Pomme", "pomme")).isTrue();
        }

        @Test
        @DisplayName("espaces autour ignorés → true")
        void trimmed() {
            assertThat(service.compare("  pomme  ", "pomme")).isTrue();
        }

        @Test
        @DisplayName("différents → false")
        void different() {
            assertThat(service.compare("poire", "pomme")).isFalse();
        }
    }

    // ── Comparaison numérique ─────────────────────────────────────────────────

    @Nested
    @DisplayName("Nombres")
    class Nombres {

        @Test
        @DisplayName("entiers égaux → true")
        void integersEqual() {
            assertThat(service.compare("42", "42")).isTrue();
        }

        @Test
        @DisplayName("entier vs double équivalent → true")
        void intVsDouble() {
            assertThat(service.compare("42", "42.0")).isTrue();
        }

        @Test
        @DisplayName("doubles dans la tolérance → true")
        void withinTolerance() {
            assertThat(service.compare("3.14159", "3.14159")).isTrue();
        }

        @Test
        @DisplayName("doubles hors tolérance → false")
        void outsideTolerance() {
            assertThat(service.compare("3.0", "4.0")).isFalse();
        }

        @Test
        @DisplayName("valeurs numériques passées comme Integer → true")
        void integerObject() {
            assertThat(service.compare(42, 42)).isTrue();
        }

        @Test
        @DisplayName("entier vs string numérique → true")
        void integerVsString() {
            assertThat(service.compare(42, "42")).isTrue();
        }

        @Test
        @DisplayName("entiers différents → false")
        void integersDifferent() {
            assertThat(service.compare(42, 43)).isFalse();
        }
    }

    // ── Comparaison fractions ─────────────────────────────────────────────────

    @Nested
    @DisplayName("Fractions")
    class Fractions {

        @Test
        @DisplayName("1/2 vs 1/2 → true")
        void sameFraction() {
            assertThat(service.compare("1/2", "1/2")).isTrue();
        }

        @Test
        @DisplayName("1/2 vs 0.5 → true")
        void fractionVsDecimal() {
            assertThat(service.compare("1/2", "0.5")).isTrue();
        }

        @Test
        @DisplayName("2/4 vs 1/2 → true (équivalentes)")
        void equivalentFractions() {
            assertThat(service.compare("2/4", "1/2")).isTrue();
        }

        @Test
        @DisplayName("3/4 vs 1/2 → false")
        void differentFractions() {
            assertThat(service.compare("3/4", "1/2")).isFalse();
        }

        @Test
        @DisplayName("fraction négative -1/2 vs -0.5 → true")
        void negativeFraction() {
            assertThat(service.compare("-1/2", "-0.5")).isTrue();
        }
    }

    // ── Comparaison listes ────────────────────────────────────────────────────

    @Nested
    @DisplayName("Listes (drag-drop, cloze — ordre strict)")
    class Listes {

        @Test
        @DisplayName("listes identiques → true")
        void same() {
            assertThat(service.compare(List.of("a", "b", "c"), List.of("a", "b", "c"))).isTrue();
        }

        @Test
        @DisplayName("ordre différent → false (ordre strict)")
        void differentOrder() {
            assertThat(service.compare(List.of("b", "a", "c"), List.of("a", "b", "c"))).isFalse();
        }

        @Test
        @DisplayName("tailles différentes → false")
        void differentSize() {
            assertThat(service.compare(List.of("a", "b"), List.of("a", "b", "c"))).isFalse();
        }

        @Test
        @DisplayName("insensible à la casse dans les listes → true")
        void caseInsensitiveInList() {
            assertThat(service.compare(List.of("Pomme", "POIRE"), List.of("pomme", "poire"))).isTrue();
        }

        @Test
        @DisplayName("liste vide vs liste vide → true")
        void emptyLists() {
            assertThat(service.compare(List.of(), List.of())).isTrue();
        }

        @Test
        @DisplayName("string seule vs liste d'un élément → true")
        void stringVsSingletonList() {
            assertThat(service.compare("pomme", List.of("pomme"))).isTrue();
        }
    }

    // ── listsEqual directement ────────────────────────────────────────────────

    @Test
    @DisplayName("listsEqual — listes égales → true")
    void listsEqualTrue() {
        assertThat(service.listsEqual(List.of("x", "y"), List.of("x", "y"))).isTrue();
    }

    @Test
    @DisplayName("listsEqual — listes différentes → false")
    void listsEqualFalse() {
        assertThat(service.listsEqual(List.of("x", "z"), List.of("x", "y"))).isFalse();
    }
}
