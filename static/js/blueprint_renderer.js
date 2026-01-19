class BlueprintRenderer {
    static render(containerId, blueprint) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        if (blueprint.type === 'pizza') {
            this.renderPizza(container, blueprint);
        } else if (blueprint.type === 'grid') {
            this.renderGrid(container, blueprint);
        } else if (blueprint.type === 'beaker') {
            this.renderBeaker(container, blueprint);
        } else {
            container.innerText = "Blueprint type unknown: " + blueprint.type;
        }
    }

    static renderPizza(container, data) {
        const size = 200;
        const cx = size / 2;
        const cy = size / 2;
        const r = size / 2 - 10;

        let svg = `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">`;

        // Background circle
        svg += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#eebb99" stroke="#885522" stroke-width="2" />`;

        const total = data.total || 8;
        const highlighted = data.highlighted || 0;
        const style = data.style || "normal"; // normal, eaten

        const angleStep = (2 * Math.PI) / total;

        for (let i = 0; i < total; i++) {
            // Calculate slice coordinates
            const startAngle = i * angleStep - Math.PI / 2;
            const endAngle = (i + 1) * angleStep - Math.PI / 2;

            const x1 = cx + r * Math.cos(startAngle);
            const y1 = cy + r * Math.sin(startAngle);
            const x2 = cx + r * Math.cos(endAngle);
            const y2 = cy + r * Math.sin(endAngle);

            // Path command for slice
            const d = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2} Z`;

            let fill = "#fff8e7"; // Cheese color
            let opacity = 1.0;

            // Check if this slice is "highlighted" / "active"
            if (i < highlighted) {
                if (style === 'eaten') {
                    fill = "#333";
                    opacity = 0.2; // Dimmed out
                } else {
                    fill = "var(--primary)"; // Selected
                }
            }

            svg += `<path d="${d}" fill="${fill}" stroke="#885522" stroke-width="1" fill-opacity="${opacity}" />`;

            // Add pepperoni if not eaten
            if (style !== 'eaten' || i >= highlighted) {
                const mx = cx + (r * 0.6) * Math.cos(startAngle + angleStep / 2);
                const my = cy + (r * 0.6) * Math.sin(startAngle + angleStep / 2);
                svg += `<circle cx="${mx}" cy="${my}" r="${r / 10}" fill="#cc3333" />`;
            }
        }

        svg += `</svg>`;
        container.innerHTML = svg;
    }

    static renderGrid(container, data) {
        // Chocolate bar style
        const rows = data.rows;
        const cols = data.cols;
        const highlighted = data.highlighted || 0;
        const style = data.style || "normal";

        const cellSize = 40;
        const width = cols * cellSize;
        const height = rows * cellSize;

        let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`;

        let count = 0;
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                count++;
                const x = c * cellSize;
                const y = r * cellSize;

                let fill = "#5c3a21"; // Chocolate
                let opacity = 1.0;

                if (count <= highlighted) {
                    if (style === 'missing') {
                        fill = "#222";
                        opacity = 0.1;
                    } else {
                        fill = "#ff9900"; // Highlighted
                    }
                }

                svg += `<rect x="${x + 2}" y="${y + 2}" width="${cellSize - 4}" height="${cellSize - 4}" rx="4" fill="${fill}" fill-opacity="${opacity}" stroke="#3d2616" stroke-width="1" />`;
            }
        }

        svg += `</svg>`;
        container.innerHTML = svg;
    }

    static renderBeaker(container, data) {
        const width = 100;
        const height = 200;

        let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`;

        // Beaker outline
        svg += `<path d="M 10 10 L 10 190 L 90 190 L 90 10" fill="none" stroke="#aaa" stroke-width="3" />`;

        const capacity = data.capacity || 500;
        const levelStart = data.level_start;
        const levelEnd = data.level_end;

        // Mapping function
        const getY = (vol) => 190 - (vol / capacity) * 180;

        // Initial liquid
        const yStart = getY(levelStart);
        svg += `<rect x="11" y="${yStart}" width="78" height="${190 - yStart}" fill="#ddf" />`;

        // Added liquid (ghost or different color)
        if (levelEnd > levelStart) {
            const yEnd = getY(levelEnd);
            const hDiff = yStart - yEnd;
            svg += `<rect x="11" y="${yEnd}" width="78" height="${hDiff}" fill="#aaf" fill-opacity="0.5" stroke="#88f" stroke-dasharray="4" />`;
        }

        // Ticks
        for (let i = 100; i < capacity; i += 100) {
            const y = getY(i);
            svg += `<line x1="10" y1="${y}" x2="20" y2="${y}" stroke="#aaa" stroke-width="1" />`;
            svg += `<text x="25" y="${y + 4}" font-size="10" fill="#aaa">${i}</text>`;
        }

        svg += `</svg>`;
        container.innerHTML = svg;
    }
}

// Export to global scope
window.BlueprintRenderer = BlueprintRenderer;
