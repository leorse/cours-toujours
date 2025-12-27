
const FractionRenderer = {
    colors: {
        "Tom": "#3498db",
        "Alice": "#e67e22",
        "Empty": "#ecf0f1",
        "PizzaCrust": "#f39c12",
        "GridLine": "#bdc3c7",
        "Border": "#7f8c8d"
    },

    render: function (containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = ''; // Clear

        // Compute visual data (normally done by backend, but we can do some here if needed)
        // Check if we received the raw Blueprint or the Exercise data.
        // If we receive the exercise data, we should probably call an API or process it.
        // But for this setup, let's assume 'data' contains the blueprint computed by server OR 
        // we replicate the logic here.
        // Wait, the plan was server generates blueprint. 
        // But the current template implementation passes 'exercise' object.
        // We need a way to get the blueprint. 
        // Option 1: Inline blueprint in template.
        // Option 2: JS logic replicates.

        // Let's replicate simple logic here because we don't have a specific API for "get blueprint" 
        // and we want it to be fast/contained.

        const type = data.visual || "CYLINDER";

        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "100%");
        svg.setAttribute("viewBox", "0 0 200 200");
        svg.style.maxWidth = "300px";
        svg.style.maxHeight = "300px";
        svg.style.display = "block";
        svg.style.margin = "0 auto";

        container.appendChild(svg);

        const blueprint = this.generateBlueprint(data);

        if (type === "PIZZA") this.drawPizza(svg, blueprint);
        else if (type === "GRID") this.drawGrid(svg, blueprint);
        else if (type === "CYLINDER") this.drawCylinder(svg, blueprint);
    },

    parseFraction: function (frac) {
        if (typeof frac === 'number') return frac;
        if (typeof frac === 'string' && frac.includes('/')) {
            const parts = frac.split('/');
            return parseInt(parts[0]) / parseInt(parts[1]);
        }
        return parseFloat(frac) || 0;
    },

    generateBlueprint: function (data) {
        const parts = data.participants || [];
        let currentOffset = 0;
        const items = parts.map(p => {
            const val = this.parseFraction(p.fraction);
            const item = {
                name: p.name,
                color: p.color || this.colors[p.name] || "#999",
                start: currentOffset,
                val: val,
                end: currentOffset + val
            };
            currentOffset += val;
            return item;
        });

        return {
            items: items,
            total_parts: data.parts || 1, // Visual divisions
            remaining: Math.max(0, 1 - currentOffset)
        };
    },

    drawPizza: function (svg, blueprint) {
        const cx = 100, cy = 100, r = 90;

        // Draw Crust/Background
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        bg.setAttribute("cx", cx);
        bg.setAttribute("cy", cy);
        bg.setAttribute("r", r);
        bg.setAttribute("fill", this.colors.Empty);
        bg.setAttribute("stroke", this.colors.PizzaCrust);
        bg.setAttribute("stroke-width", "4");
        svg.appendChild(bg);

        // Draw Slices
        blueprint.items.forEach(item => {
            const startAngle = item.start * 360;
            const endAngle = item.end * 360;

            // Convert polar to cartesian
            // -90 degrees offset to start at top
            const x1 = cx + r * Math.cos(Math.PI * (startAngle - 90) / 180);
            const y1 = cy + r * Math.sin(Math.PI * (startAngle - 90) / 180);
            const x2 = cx + r * Math.cos(Math.PI * (endAngle - 90) / 180);
            const y2 = cy + r * Math.sin(Math.PI * (endAngle - 90) / 180);

            const largeArc = (endAngle - startAngle) > 180 ? 1 : 0;

            const pathData = [
                `M ${cx} ${cy}`,
                `L ${x1} ${y1}`,
                `A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`,
                `Z`
            ].join(" ");

            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute("d", pathData);
            path.setAttribute("fill", item.color);
            path.setAttribute("stroke", "#fff");
            path.setAttribute("stroke-width", "2");
            svg.appendChild(path);
        });

        // Draw division lines if total_parts defined
        if (blueprint.total_parts > 1) {
            for (let i = 0; i < blueprint.total_parts; i++) {
                const angle = (i / blueprint.total_parts) * 360;
                const x = cx + r * Math.cos(Math.PI * (angle - 90) / 180);
                const y = cy + r * Math.sin(Math.PI * (angle - 90) / 180);

                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", cx);
                line.setAttribute("y1", cy);
                line.setAttribute("x2", x);
                line.setAttribute("y2", y);
                line.setAttribute("stroke", "rgba(0,0,0,0.2)");
                line.setAttribute("stroke-width", "1");
                svg.appendChild(line);
            }
        }
    },

    drawGrid: function (svg, blueprint) {
        // Assume 200x200 box
        // Best fit grid
        const n = blueprint.total_parts;
        let rows = 1, cols = n;

        // Simple factorizer
        const sqrt = Math.ceil(Math.sqrt(n));
        for (let i = sqrt; i > 0; i--) {
            if (n % i === 0) {
                rows = i;
                cols = n / i;
                break;
            }
        }

        // If prime or weird, just do square-ish? No, stick to divisions. 
        // If n is large (1000), this might fail. "total_units" vs "parts".
        // Use 'parts' for grid.

        const w = 180 / cols;
        const h = 180 / rows;
        const offX = 10;
        const offY = 10;

        // Background
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        bg.setAttribute("x", offX);
        bg.setAttribute("y", offY);
        bg.setAttribute("width", 180);
        bg.setAttribute("height", 180);
        bg.setAttribute("fill", "white"); // or chocolate color?
        bg.setAttribute("stroke", "#555");
        svg.appendChild(bg);

        // Cells
        let cellIdx = 0;
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const cellX = offX + c * w;
                const cellY = offY + r * h;

                // Determine color
                let color = this.colors.Empty;

                // Find who owns this cell
                // We map cellIdx / total_parts to see if it falls in range
                // A bit rough for exact fractions but works for unit parts

                const cellCenterP = (cellIdx + 0.5) / n;

                for (let item of blueprint.items) {
                    if (cellCenterP >= item.start && cellCenterP <= item.end) {
                        color = item.color;
                        break;
                    }
                }

                const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                rect.setAttribute("x", cellX);
                rect.setAttribute("y", cellY);
                rect.setAttribute("width", w);
                rect.setAttribute("height", h);
                rect.setAttribute("fill", color);
                rect.setAttribute("stroke", "#eee");
                svg.appendChild(rect);

                cellIdx++;
            }
        }
    },

    drawCylinder: function (svg, blueprint) {
        // Draw a beaker/container style
        const x = 60, y = 20, w = 80, h = 160;

        // Background (empty)
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        bg.setAttribute("x", x);
        bg.setAttribute("y", y);
        bg.setAttribute("width", w);
        bg.setAttribute("height", h);
        bg.setAttribute("fill", "#fcfcfc");
        bg.setAttribute("stroke", "#333");
        bg.setAttribute("stroke-width", "3");
        bg.setAttribute("rx", "5"); // rounded corners
        svg.appendChild(bg);

        // Fill levels
        // We stack from bottom up
        let currentY = y + h;

        blueprint.items.forEach(item => {
            const fillHeight = item.val * h;
            currentY -= fillHeight;

            const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("x", x + 2); // padding
            rect.setAttribute("y", currentY);
            rect.setAttribute("width", w - 4);
            rect.setAttribute("height", fillHeight);
            rect.setAttribute("fill", item.color);
            rect.setAttribute("stroke", "none");

            // Simple wave effect on top? simplified for now
            svg.appendChild(rect);
        });

        // Graduations
        const steps = blueprint.total_parts;
        if (steps < 20) {
            for (let i = 1; i < steps; i++) {
                const gradY = y + h - (i / steps) * h;
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", x);
                line.setAttribute("y1", gradY);
                line.setAttribute("x2", x + 15);
                line.setAttribute("y2", gradY);
                line.setAttribute("stroke", "#333");
                line.setAttribute("stroke-width", "2");
                svg.appendChild(line);

                // Right side too
                const line2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line2.setAttribute("x1", x + w - 15);
                line2.setAttribute("y1", gradY);
                line2.setAttribute("x2", x + w);
                line2.setAttribute("y2", gradY);
                line2.setAttribute("stroke", "#333");
                line2.setAttribute("stroke-width", "2");
                svg.appendChild(line2);
            }
        }
    }
};

window.FractionRenderer = FractionRenderer;
