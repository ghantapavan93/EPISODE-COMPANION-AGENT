/**
 * Kochi Ultimate Background - All 4 Styles Combined
 * Neural Constellation + Liquid Gradient + Holographic Grid + Aurora Waves
 */

class KochiUltimateBackground {
    constructor() {
        this.canvas = document.getElementById('kochiCanvas');
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.gridLines = [];
        this.mouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
        this.frame = 0;

        this.resize();
        this.createParticles();
        this.createGrid();
        this.bindEvents();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.particles = [];
        this.createParticles();
    }

    createParticles() {
        const count = Math.min(120, Math.floor((this.canvas.width * this.canvas.height) / 12000));

        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                radius: Math.random() * 2.5 + 0.5,
                hue: Math.random() * 80 + 180, // Blue to purple to pink
                alpha: Math.random() * 0.6 + 0.3,
                pulsePhase: Math.random() * Math.PI * 2,
                pulseSpeed: 0.01 + Math.random() * 0.02
            });
        }
    }

    createGrid() {
        // Sparse grid lines for holographic effect
        const spacing = 100;
        for (let i = 0; i < this.canvas.width / spacing; i++) {
            if (Math.random() > 0.6) {
                this.gridLines.push({
                    vertical: true,
                    position: i * spacing,
                    opacity: Math.random() * 0.3 + 0.1
                });
            }
        }
        for (let i = 0; i < this.canvas.height / spacing; i++) {
            if (Math.random() > 0.6) {
                this.gridLines.push({
                    vertical: false,
                    position: i * spacing,
                    opacity: Math.random() * 0.3 + 0.1
                });
            }
        }
    }

    bindEvents() {
        window.addEventListener('resize', () => this.resize());

        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        // Touch support
        document.addEventListener('touchmove', (e) => {
            if (e.touches[0]) {
                this.mouse.x = e.touches[0].clientX;
                this.mouse.y = e.touches[0].clientY;
            }
        });
    }

    drawLiquidGradient() {
        // Animated liquid gradient base
        const phase = this.frame * 0.001;

        const gradient = this.ctx.createLinearGradient(
            0, 0,
            this.canvas.width, this.canvas.height
        );

        // Shifting colors
        const hue1 = 220 + Math.sin(phase) * 20;
        const hue2 = 260 + Math.cos(phase * 1.3) * 25;
        const hue3 = 290 + Math.sin(phase * 0.7) * 15;

        gradient.addColorStop(0, `hsla(${hue1}, 70%, 25%, 0.4)`);
        gradient.addColorStop(0.5, `hsla(${hue2}, 65%, 30%, 0.5)`);
        gradient.addColorStop(1, `hsla(${hue3}, 60%, 28%, 0.4)`);

        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    drawAuroraWaves() {
        // Multiple flowing aurora waves
        const waves = 4;

        for (let w = 0; w < waves; w++) {
            this.ctx.beginPath();

            const phase = this.frame * 0.003 + w * Math.PI * 0.5;
            const amplitude = 60 + w * 10;
            const frequency = 0.002 + w * 0.0005;
            const yOffset = this.canvas.height * (0.3 + w * 0.15);

            for (let x = 0; x <= this.canvas.width; x += 3) {
                const y = yOffset +
                    Math.sin(x * frequency + phase) * amplitude +
                    Math.sin(x * frequency * 2 + phase * 1.5) * (amplitude * 0.5);

                if (x === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    this.ctx.lineTo(x, y);
                }
            }

            // Aurora glow effect
            const hue = 180 + w * 20 + Math.sin(phase) * 30;
            const gradient = this.ctx.createLinearGradient(0, yOffset - 100, 0, yOffset + 100);
            gradient.addColorStop(0, `hsla(${hue}, 80%, 60%, 0)`);
            gradient.addColorStop(0.5, `hsla(${hue}, 80%, 55%, 0.15)`);
            gradient.addColorStop(1, `hsla(${hue}, 80%, 50%, 0)`);

            this.ctx.strokeStyle = gradient;
            this.ctx.lineWidth = 3 + w;
            this.ctx.stroke();
        }
    }

    drawHolographicGrid() {
        // Subtle holographic grid lines
        this.gridLines.forEach(line => {
            const pulse = Math.sin(this.frame * 0.01) * 0.5 + 0.5;
            const alpha = line.opacity * (0.5 + pulse * 0.5);

            this.ctx.strokeStyle = `rgba(100, 200, 255, ${alpha * 0.3})`;
            this.ctx.lineWidth = 1;

            this.ctx.beginPath();
            if (line.vertical) {
                this.ctx.moveTo(line.position, 0);
                this.ctx.lineTo(line.position, this.canvas.height);
            } else {
                this.ctx.moveTo(0, line.position);
                this.ctx.lineTo(this.canvas.width, line.position);
            }
            this.ctx.stroke();
        });
    }

    drawParticleConnections() {
        // Neural network connections
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const p1 = this.particles[i];
                const p2 = this.particles[j];

                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 180) {
                    const opacity = (1 - distance / 180) * 0.4;
                    const avgHue = (p1.hue + p2.hue) / 2;

                    const gradient = this.ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y);
                    gradient.addColorStop(0, `hsla(${p1.hue}, 80%, 65%, ${opacity})`);
                    gradient.addColorStop(1, `hsla(${p2.hue}, 80%, 65%, ${opacity})`);

                    this.ctx.strokeStyle = gradient;
                    this.ctx.lineWidth = 1.5;
                    this.ctx.beginPath();
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                }
            }
        }
    }

    drawParticles() {
        this.particles.forEach(p => {
            // Pulsing effect
            const pulse = Math.sin(this.frame * p.pulseSpeed + p.pulsePhase) * 0.5 + 0.5;
            const currentRadius = p.radius * (1 + pulse * 0.6);

            // Outer glow
            const glowGradient = this.ctx.createRadialGradient(
                p.x, p.y, 0,
                p.x, p.y, currentRadius * 4
            );
            glowGradient.addColorStop(0, `hsla(${p.hue}, 90%, 70%, ${p.alpha * 0.8})`);
            glowGradient.addColorStop(0.4, `hsla(${p.hue}, 85%, 60%, ${p.alpha * 0.4})`);
            glowGradient.addColorStop(1, `hsla(${p.hue}, 80%, 50%, 0)`);

            this.ctx.fillStyle = glowGradient;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, currentRadius * 4, 0, Math.PI * 2);
            this.ctx.fill();

            // Core particle
            this.ctx.fillStyle = `hsla(${p.hue}, 95%, 85%, ${p.alpha})`;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, currentRadius, 0, Math.PI * 2);
            this.ctx.fill();

            // Bright center
            this.ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha * 0.6})`;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, currentRadius * 0.4, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }

    updateParticles() {
        this.particles.forEach(p => {
            // Movement
            p.x += p.vx;
            p.y += p.vy;

            // Mouse interaction (repulsion)
            const dx = this.mouse.x - p.x;
            const dy = this.mouse.y - p.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 250) {
                const force = (250 - distance) / 250;
                const angle = Math.atan2(dy, dx);
                p.vx -= Math.cos(angle) * force * 0.15;
                p.vy -= Math.sin(angle) * force * 0.15;
            }

            // Gentle drift
            p.vx += (Math.random() - 0.5) * 0.03;
            p.vy += (Math.random() - 0.5) * 0.03;

            // Damping (smooth deceleration)
            p.vx *= 0.98;
            p.vy *= 0.98;

            // Speed limit
            const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            if (speed > 2) {
                p.vx = (p.vx / speed) * 2;
                p.vy = (p.vy / speed) * 2;
            }

            // Wrap around edges with margin
            const margin = 50;
            if (p.x < -margin) p.x = this.canvas.width + margin;
            if (p.x > this.canvas.width + margin) p.x = -margin;
            if (p.y < -margin) p.y = this.canvas.height + margin;
            if (p.y > this.canvas.height + margin) p.y = -margin;

            // Subtle color shift
            p.hue += 0.05;
            if (p.hue > 280) p.hue = 180;
        });
    }

    animate() {
        this.frame++;

        // Clear with dark base
        this.ctx.fillStyle = '#0a0e27';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Layer 1: Liquid gradient (bottom)
        this.drawLiquidGradient();

        // Layer 2: Aurora waves
        this.drawAuroraWaves();

        // Layer 3: Holographic grid
        this.drawHolographicGrid();

        // Layer 4: Neural connections
        this.drawParticleConnections();

        // Layer 5: Particles (top)
        this.updateParticles();
        this.drawParticles();

        requestAnimationFrame(() => this.animate());
    }
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new KochiUltimateBackground();
    });
} else {
    new KochiUltimateBackground();
}
