/**
 * touch_dragdrop.js — Drag-drop tactile (tap-sélect-tap)
 *
 * Sur écrans tactiles, le drag HTML5 ne fonctionne pas (iOS/Android).
 * Ce module remplace le drag-drop par un pattern :
 *   1. Tap sur .draggable-item  → sélectionne l'élément (surlignage)
 *   2. Tap sur .drop-zone       → place l'élément dans la zone
 *   3. Tap sur le même item     → désélectionne
 *
 * Utilisation :
 *   TouchDragDrop.init(containerEl, onPlace)
 *   onPlace(zoneEl, value, zoneId) est appelé à chaque dépôt.
 *
 * Détection : pointer: coarse (touch-primary devices uniquement)
 * Pas de UA sniffing.
 */
(function () {
    'use strict';

    function initTouchDragDrop(containerEl, onPlace) {
        // Seulement sur appareils tactiles principaux
        if (!window.matchMedia('(pointer: coarse)').matches) return;

        let selectedEl = null;
        let selectedValue = null;

        containerEl.addEventListener('click', function (e) {
            const item = e.target.closest('.draggable-item');
            const zone = e.target.closest('.drop-zone');

            if (item) {
                // Élément déjà verrouillé (après readonly) — ignorer
                if (item.draggable === false || item.getAttribute('draggable') === 'false') return;

                if (selectedEl === item) {
                    // Deuxième tap sur le même : désélectionner
                    deselect();
                    return;
                }

                // Sélectionner ce nouvel élément
                deselect();
                selectedEl = item;
                selectedValue = item.textContent.trim();
                item.classList.add('touch-selected');

                // Illuminer les zones disponibles
                containerEl.querySelectorAll('.drop-zone').forEach(z => {
                    if (z.style.pointerEvents !== 'none') {
                        z.classList.add('touch-ready');
                    }
                });
                return;
            }

            if (zone && selectedEl !== null) {
                // Zone verrouillée — ignorer
                if (zone.style.pointerEvents === 'none') return;

                // Déposer la valeur
                zone.textContent = selectedValue;
                zone.classList.add('filled');
                zone.classList.remove('touch-ready');

                containerEl.querySelectorAll('.drop-zone').forEach(z => z.classList.remove('touch-ready'));

                if (typeof onPlace === 'function') {
                    onPlace(zone, selectedValue, zone.id);
                }

                deselect();
            }
        });

        function deselect() {
            if (selectedEl) {
                selectedEl.classList.remove('touch-selected');
                containerEl.querySelectorAll('.drop-zone').forEach(z => z.classList.remove('touch-ready'));
            }
            selectedEl = null;
            selectedValue = null;
        }
    }

    window.TouchDragDrop = { init: initTouchDragDrop };
})();
