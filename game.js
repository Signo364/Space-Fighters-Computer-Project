const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const WIDTH = 900;
const HEIGHT = 500;
canvas.width = WIDTH;
canvas.height = HEIGHT;

const WHITE = '#FFFFFF';
const BLACK = '#000000';
const RED = '#FF3C3C';
const YELLOW = '#FFFF3C';
const CYAN = '#00FFFF';
const NEON_BLUE = '#3296FF';
const NEON_PINK = '#FF32B4';
const ELECTRIC_BLUE = '#64C8FF';

const FPS = 60;
const VEL = 5;
const BULLETS_VEL = 10;
const MAX_BULLETS = 3;
const SPACESHIP_WIDTH = 55;
const SPACESHIP_HEIGHT = 40;

let gameState = 'control-select';
let controlScheme = 1;
let gameTime = 0;
let screenShake = 0;

let yellowShip, redShip;
let yellowBullets = [];
let redBullets = [];
let yellowHealth = 10;
let redHealth = 10;
let yellowFlash = 0;
let redFlash = 0;

let particles = [];
let energyRings = [];
let stars = [];
let shootingStars = [];
let nebulaClouds = [];

let keys = {};
let mouseX = 0;
let mouseY = 0;
let mouseDown = false;

let assetsLoaded = 0;
const totalAssets = 2;
const yellowShipImg = new Image();
const redShipImg = new Image();

yellowShipImg.onload = () => {
    assetsLoaded++;
    checkAssetsLoaded();
};
redShipImg.onload = () => {
    assetsLoaded++;
    checkAssetsLoaded();
};

yellowShipImg.src = 'Assets/spaceship_yellow.png';
redShipImg.src = 'Assets/spaceship_red.png';

function checkAssetsLoaded() {
    if (assetsLoaded === totalAssets) {
        document.getElementById('loading').style.opacity = '0';
        setTimeout(() => {
            document.getElementById('loading').style.display = 'none';
        }, 500);
    }
}

class Star {
    constructor(layer = 1) {
        this.layer = layer;
        this.x = Math.random() * WIDTH;
        this.y = Math.random() * HEIGHT;
        this.speed = (0.3 + Math.random() * 1.0) * layer;
        this.size = Math.max(1, Math.random() * 2 + layer * 0.5);
        this.brightness = 150 + Math.random() * 105;
        this.twinkleSpeed = Math.random() * 0.15 + 0.05;
        this.twinkleOffset = Math.random() * Math.PI * 2;
    }

    update() {
        this.x -= this.speed;
        if (this.x < -5) {
            this.x = WIDTH + Math.random() * 50;
            this.y = Math.random() * HEIGHT;
        }
    }

    draw() {
        const twinkle = Math.sin(gameTime * this.twinkleSpeed + this.twinkleOffset) * 0.4 + 0.6;
        const brightness = this.brightness * twinkle;
        ctx.fillStyle = `rgba(${brightness}, ${brightness}, ${brightness}, ${twinkle})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

class ShootingStar {
    constructor() {
        this.active = false;
        this.x = 0;
        this.y = 0;
        this.vx = 0;
        this.vy = 0;
        this.length = 0;
        this.lifetime = 0;
    }

    spawn() {
        this.active = true;
        this.x = WIDTH / 2 + Math.random() * (WIDTH / 2);
        this.y = Math.random() * (HEIGHT / 3);
        const speed = 15 + Math.random() * 10;
        const angle = Math.random() * 0.5 + 0.2;
        this.vx = -speed * Math.cos(angle);
        this.vy = speed * Math.sin(angle);
        this.length = 30 + Math.random() * 30;
        this.lifetime = 60;
    }

    update() {
        if (this.active) {
            this.x += this.vx;
            this.y += this.vy;
            this.lifetime--;
            if (this.lifetime <= 0 || this.x < -50 || this.y > HEIGHT + 50) {
                this.active = false;
            }
        }
    }

    draw() {
        if (this.active) {
            const alpha = this.lifetime / 60;
            for (let i = 0; i < this.length; i++) {
                const t = i / this.length;
                const px = this.x - this.vx * t * 0.5;
                const py = this.y - this.vy * t * 0.5;
                const brightness = 255 * (1 - t) * alpha;
                const size = Math.max(1, 3 * (1 - t));
                ctx.fillStyle = `rgba(${brightness}, ${brightness}, ${brightness}, ${alpha})`;
                ctx.beginPath();
                ctx.arc(px, py, size, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
}

class Particle {
    constructor(x, y, color, vx, vy, size = 3, lifetime = 30, gravity = 0) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.vx = vx;
        this.vy = vy;
        this.size = size;
        this.originalSize = size;
        this.lifetime = lifetime;
        this.maxLifetime = lifetime;
        this.gravity = gravity;
        this.alive = true;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += this.gravity;
        this.vx *= 0.99;
        this.vy *= 0.99;
        this.lifetime--;
        this.size = this.originalSize * (this.lifetime / this.maxLifetime);
        if (this.lifetime <= 0) {
            this.alive = false;
        }
    }

    draw() {
        if (this.alive && this.size > 0.5) {
            const alpha = this.lifetime / this.maxLifetime;
            ctx.fillStyle = this.color.replace('1)', `${alpha})`);
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}

class EnergyRing {
    constructor(x, y, color, maxRadius = 100, speed = 3) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.radius = 5;
        this.maxRadius = maxRadius;
        this.speed = speed;
        this.alive = true;
    }

    update() {
        this.radius += this.speed;
        if (this.radius > this.maxRadius) {
            this.alive = false;
        }
    }

    draw() {
        if (this.alive) {
            const alpha = 1 - (this.radius / this.maxRadius);
            ctx.strokeStyle = this.color.replace('1)', `${alpha})`);
            ctx.lineWidth = Math.max(1, 3 * alpha);
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
}

function createExplosion(x, y, color, count = 25) {
    energyRings.push(new EnergyRing(x, y, color, 80, 4));
    energyRings.push(new EnergyRing(x, y, WHITE, 50, 6));

    for (let i = 0; i < count; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 5 + 2;
        const vx = Math.cos(angle) * speed;
        const vy = Math.sin(angle) * speed;
        const size = 2 + Math.random() * 4;
        particles.push(new Particle(x, y, color, vx, vy, size, 25 + Math.random() * 25, 0.08));
    }
}

function createHitEffect(x, y, color) {
    screenShake = 12;
    energyRings.push(new EnergyRing(x, y, color, 60, 5));
    createExplosion(x, y, color, 20);
}

function createVictoryExplosion(x, y, color) {
    for (let i = 0; i < 5; i++) {
        const delayRadius = 30 + i * 40;
        energyRings.push(new EnergyRing(x, y, color, delayRadius + 60, 3 + i));
    }

    const colors = [color, CYAN, NEON_PINK, WHITE];
    for (let ring = 0; ring < 4; ring++) {
        for (let i = 0; i < 25; i++) {
            const angle = (i / 25) * Math.PI * 2 + ring * 0.3;
            const speed = 4 + ring * 2.5;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;
            particles.push(new Particle(x, y, colors[ring % 4], vx, vy, 5, 60 + ring * 15));
        }
    }
}

function initStars() {
    stars = [];
    for (let i = 0; i < 60; i++) stars.push(new Star(1));
    for (let i = 0; i < 35; i++) stars.push(new Star(2));
    for (let i = 0; i < 20; i++) stars.push(new Star(3));
}

function initShootingStars() {
    shootingStars = [];
    for (let i = 0; i < 3; i++) {
        shootingStars.push(new ShootingStar());
    }
}

function initNebula() {
    nebulaClouds = [];
    for (let i = 0; i < 8; i++) {
        nebulaClouds.push({
            x: Math.random() * WIDTH,
            y: Math.random() * HEIGHT,
            size: 100 + Math.random() * 150,
            speed: Math.random() * 0.3 + 0.1,
            hue: Math.random() * 60 + 200
        });
    }
}

function drawBackground() {
    const gradient = ctx.createLinearGradient(0, 0, 0, HEIGHT);
    gradient.addColorStop(0, '#050515');
    gradient.addColorStop(0.5, '#0A0A20');
    gradient.addColorStop(1, '#050515');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    nebulaClouds.forEach(cloud => {
        cloud.x -= cloud.speed;
        if (cloud.x < -cloud.size) {
            cloud.x = WIDTH + cloud.size;
            cloud.y = Math.random() * HEIGHT;
        }

        const gradient = ctx.createRadialGradient(cloud.x, cloud.y, 0, cloud.x, cloud.y, cloud.size);
        gradient.addColorStop(0, `hsla(${cloud.hue}, 70%, 20%, 0.15)`);
        gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient;
        ctx.fillRect(cloud.x - cloud.size, cloud.y - cloud.size, cloud.size * 2, cloud.size * 2);
    });

    stars.forEach(star => {
        star.update();
        star.draw();
    });

    if (Math.random() < 0.01) {
        const inactive = shootingStars.find(s => !s.active);
        if (inactive) inactive.spawn();
    }

    shootingStars.forEach(star => {
        star.update();
        star.draw();
    });
}

function drawBorder() {
    const pulse = Math.sin(gameTime * 0.08) * 0.4 + 0.6;
    const borderX = WIDTH / 2 - 5;

    for (let i = 12; i > 0; i -= 2) {
        const glow = pulse / (i * 0.5);
        ctx.strokeStyle = `rgba(0, ${180 * glow}, ${255 * glow}, ${glow * 0.3})`;
        ctx.lineWidth = i * 2;
        ctx.beginPath();
        ctx.moveTo(borderX, 0);
        ctx.lineTo(borderX, HEIGHT);
        ctx.stroke();
    }

    ctx.strokeStyle = WHITE;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(borderX, 0);
    ctx.lineTo(borderX, HEIGHT);
    ctx.stroke();
}

function drawNeonText(text, x, y, fontSize, color, align = 'center') {
    ctx.font = `bold ${fontSize}px Arial, sans-serif`;
    ctx.textAlign = align;
    ctx.textBaseline = 'middle';

    for (let i = 3; i > 0; i--) {
        ctx.shadowBlur = i * 10;
        ctx.shadowColor = color;
        ctx.fillStyle = color;
        ctx.fillText(text, x, y);
    }
    ctx.shadowBlur = 0;
}

function drawHealthBar(x, y, health, maxHealth, width, height, color) {
    ctx.fillStyle = 'rgba(20, 20, 30, 0.8)';
    ctx.fillRect(x - 3, y - 3, width + 6, height + 6);

    ctx.fillStyle = 'rgba(40, 40, 50, 1)';
    ctx.fillRect(x, y, width, height);

    const healthWidth = (health / maxHealth) * width;
    if (healthWidth > 0) {
        const gradient = ctx.createLinearGradient(x, y, x, y + height);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, color.replace('1)', '0.6)'));
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, healthWidth, height);

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, width, height);
    }
}

function drawAmmoDisplay(x, y, currentAmmo, maxAmmo, color) {
    for (let i = 0; i < maxAmmo; i++) {
        const bulletX = x + i * 18;
        if (i < currentAmmo) {
            ctx.fillStyle = color;
            ctx.fillRect(bulletX, y, 12, 8);
            ctx.fillStyle = WHITE;
            ctx.fillRect(bulletX, y, 12, 3);
        } else {
            ctx.strokeStyle = 'rgba(50, 50, 60, 1)';
            ctx.lineWidth = 1;
            ctx.strokeRect(bulletX, y, 12, 8);
        }
    }
}

function drawControlSelectScreen() {
    drawBackground();

    const titleY = 50 + Math.sin(gameTime * 0.04) * 8;
    drawNeonText('SELECT CONTROLS', WIDTH / 2, titleY, 60, CYAN);

    const boxWidth = 380;
    const boxHeight = 130;
    const boxX = WIDTH / 2 - boxWidth / 2;
    const box1Y = 160;
    const box2Y = 310;

    ctx.fillStyle = 'rgba(15, 30, 50, 0.9)';
    ctx.fillRect(boxX, box1Y, boxWidth, boxHeight);
    ctx.strokeStyle = NEON_BLUE;
    ctx.lineWidth = 2;
    ctx.strokeRect(boxX, box1Y, boxWidth, boxHeight);

    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'left';
    ctx.fillStyle = NEON_BLUE;
    ctx.fillText('Press 1: Arrow Keys', boxX + 30, box1Y + 30);
    ctx.font = '20px Arial';
    ctx.fillStyle = WHITE;
    ctx.fillText('Move: Arrow Keys', boxX + 30, box1Y + 70);
    ctx.fillText('Shoot: Right Ctrl', boxX + 30, box1Y + 100);

    ctx.fillStyle = 'rgba(40, 15, 50, 0.9)';
    ctx.fillRect(boxX, box2Y, boxWidth, boxHeight);
    ctx.strokeStyle = NEON_PINK;
    ctx.lineWidth = 2;
    ctx.strokeRect(boxX, box2Y, boxWidth, boxHeight);

    ctx.font = 'bold 24px Arial';
    ctx.fillStyle = NEON_PINK;
    ctx.fillText('Press 2: Mouse Control', boxX + 30, box2Y + 30);
    ctx.font = '20px Arial';
    ctx.fillStyle = WHITE;
    ctx.fillText('Move: Mouse Position', boxX + 30, box2Y + 70);
    ctx.fillText('Shoot: Left Click', boxX + 30, box2Y + 100);
}

function drawStartScreen() {
    drawBackground();

    const titleY = 60 + Math.sin(gameTime * 0.04) * 10;
    drawNeonText('SPACE BATTLE', WIDTH / 2, titleY, 80, CYAN);

    const subtitle = Math.sin(gameTime * 0.1);
    const subtitleColor = `rgba(${255 * subtitle + 100}, ${50 * subtitle + 100}, ${255 * (1 - subtitle) + 200}, 1)`;
    drawNeonText('NEON EDITION', WIDTH / 2, titleY + 60, 24, subtitleColor);

    const blink = Math.sin(gameTime * 0.12) * 0.5 + 0.5;
    ctx.font = '20px Arial';
    ctx.textAlign = 'center';
    ctx.fillStyle = `rgba(${blink * 255}, ${blink * 255}, ${blink * 255}, 1)`;
    ctx.fillText('Press SPACE to Start', WIDTH / 2, 220);

    const boxX = WIDTH / 2 - 200;
    const boxY = 260;
    ctx.fillStyle = 'rgba(20, 20, 35, 0.8)';
    ctx.fillRect(boxX, boxY, 400, 110);
    ctx.strokeStyle = 'rgba(60, 60, 90, 1)';
    ctx.lineWidth = 2;
    ctx.strokeRect(boxX, boxY, 400, 110);

    ctx.font = '18px Arial';
    ctx.fillStyle = YELLOW;
    ctx.fillText('Yellow: WASD + Left Ctrl', WIDTH / 2, boxY + 30);

    ctx.fillStyle = RED;
    if (controlScheme === 1) {
        ctx.fillText('Red: Arrows + Right Ctrl', WIDTH / 2, boxY + 70);
    } else {
        ctx.fillText('Red: Mouse + Left Click', WIDTH / 2, boxY + 70);
    }

    ctx.font = '14px Arial';
    ctx.fillStyle = 'rgba(120, 120, 140, 1)';
    ctx.fillText('Press C to change controls', WIDTH / 2, 390);

    const shipFloatY = Math.sin(gameTime * 0.06) * 15;
    ctx.drawImage(yellowShipImg, 80, 180 + shipFloatY, SPACESHIP_WIDTH, SPACESHIP_HEIGHT);
    ctx.drawImage(redShipImg, WIDTH - 130, 180 - shipFloatY, SPACESHIP_WIDTH, SPACESHIP_HEIGHT);
}

function drawGameplay() {
    drawBackground();
    drawBorder();

    energyRings.forEach((ring, i) => {
        ring.update();
        if (!ring.alive) {
            energyRings.splice(i, 1);
        } else {
            ring.draw();
        }
    });

    particles.forEach((particle, i) => {
        particle.update();
        if (!particle.alive) {
            particles.splice(i, 1);
        } else {
            particle.draw();
        }
    });

    yellowBullets.forEach(bullet => {
        ctx.fillStyle = YELLOW;
        ctx.shadowBlur = 10;
        ctx.shadowColor = YELLOW;
        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
        ctx.shadowBlur = 0;
    });

    redBullets.forEach(bullet => {
        ctx.fillStyle = RED;
        ctx.shadowBlur = 10;
        ctx.shadowColor = RED;
        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
        ctx.shadowBlur = 0;
    });

    if (yellowFlash > 0) {
        ctx.fillStyle = `rgba(255, 255, 200, ${yellowFlash / 10})`;
        ctx.fillRect(yellowShip.x - 5, yellowShip.y - 5, SPACESHIP_WIDTH + 10, SPACESHIP_HEIGHT + 10);
    }
    ctx.drawImage(yellowShipImg, yellowShip.x, yellowShip.y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT);

    if (redFlash > 0) {
        ctx.fillStyle = `rgba(255, 200, 200, ${redFlash / 10})`;
        ctx.fillRect(redShip.x - 5, redShip.y - 5, SPACESHIP_WIDTH + 10, SPACESHIP_HEIGHT + 10);
    }
    ctx.drawImage(redShipImg, redShip.x, redShip.y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT);

    drawHealthBar(15, 15, yellowHealth, 10, 160, 22, YELLOW);
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'left';
    ctx.fillStyle = YELLOW;
    ctx.fillText('YELLOW', 15, 50);

    drawHealthBar(WIDTH - 175, 15, redHealth, 10, 160, 22, RED);
    ctx.textAlign = 'right';
    ctx.fillStyle = RED;
    ctx.fillText('RED', WIDTH - 15, 50);

    const yellowAmmo = MAX_BULLETS - yellowBullets.length;
    const redAmmo = MAX_BULLETS - redBullets.length;
    drawAmmoDisplay(15, 65, yellowAmmo, MAX_BULLETS, YELLOW);
    drawAmmoDisplay(WIDTH - 69, 65, redAmmo, MAX_BULLETS, RED);
}

function drawWinner(text, color) {
    drawBackground();
    drawBorder();

    energyRings.forEach((ring, i) => {
        ring.update();
        if (!ring.alive) {
            energyRings.splice(i, 1);
        } else {
            ring.draw();
        }
    });

    particles.forEach((particle, i) => {
        particle.update();
        if (!particle.alive) {
            particles.splice(i, 1);
        } else {
            particle.draw();
        }
    });

    const boxWidth = 550;
    const boxHeight = 220;
    const boxX = WIDTH / 2 - boxWidth / 2;
    const boxY = HEIGHT / 2 - boxHeight / 2;

    ctx.fillStyle = 'rgba(15, 15, 25, 0.95)';
    ctx.fillRect(boxX, boxY, boxWidth, boxHeight);
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);

    const pulse = Math.sin(gameTime * 0.1) * 0.1 + 0.9;
    const pulseColor = color.replace('1)', `${pulse})`);
    drawNeonText(text, WIDTH / 2, HEIGHT / 2 - 20, 70, pulseColor);

    const blink = Math.sin(gameTime * 0.12) * 0.5 + 0.5;
    ctx.font = '18px Arial';
    ctx.textAlign = 'center';
    ctx.fillStyle = `rgba(${blink * 255}, ${blink * 255}, ${blink * 255}, 1)`;
    ctx.fillText('R - Restart  |  ESC - Quit', WIDTH / 2, HEIGHT / 2 + 50);
}

function resetGame() {
    yellowShip = { x: 100, y: 300 };
    redShip = { x: 700, y: 300 };
    yellowBullets = [];
    redBullets = [];
    yellowHealth = 10;
    redHealth = 10;
    yellowFlash = 0;
    redFlash = 0;
    particles = [];
    energyRings = [];
}

function updateGameplay() {
    if (yellowFlash > 0) yellowFlash--;
    if (redFlash > 0) redFlash--;

    if (keys['KeyA'] && yellowShip.x - VEL > 0) yellowShip.x -= VEL;
    if (keys['KeyD'] && yellowShip.x + VEL + SPACESHIP_WIDTH < WIDTH / 2 - 5) yellowShip.x += VEL;
    if (keys['KeyW'] && yellowShip.y - VEL > 0) yellowShip.y -= VEL;
    if (keys['KeyS'] && yellowShip.y + VEL + SPACESHIP_HEIGHT < HEIGHT) yellowShip.y += VEL;

    if (controlScheme === 1) {
        if (keys['ArrowLeft'] && redShip.x - VEL > WIDTH / 2 + 5) redShip.x -= VEL;
        if (keys['ArrowRight'] && redShip.x + VEL + SPACESHIP_WIDTH < WIDTH) redShip.x += VEL;
        if (keys['ArrowUp'] && redShip.y - VEL > 0) redShip.y -= VEL;
        if (keys['ArrowDown'] && redShip.y + VEL + SPACESHIP_HEIGHT < HEIGHT) redShip.y += VEL;
    } else {
        if (mouseX > WIDTH / 2 + 5) {
            const redCenterX = redShip.x + SPACESHIP_WIDTH / 2;
            const redCenterY = redShip.y + SPACESHIP_HEIGHT / 2;

            if (redCenterX < mouseX - 10 && redShip.x + VEL + SPACESHIP_WIDTH < WIDTH) {
                redShip.x += VEL;
            } else if (redCenterX > mouseX + 10 && redShip.x - VEL > WIDTH / 2 + 5) {
                redShip.x -= VEL;
            }

            if (redCenterY < mouseY - 10 && redShip.y + VEL + SPACESHIP_HEIGHT < HEIGHT) {
                redShip.y += VEL;
            } else if (redCenterY > mouseY + 10 && redShip.y - VEL > 0) {
                redShip.y -= VEL;
            }
        }
    }

    yellowBullets.forEach((bullet, i) => {
        bullet.x += BULLETS_VEL;
        if (bullet.x + bullet.width >= redShip.x &&
            bullet.x <= redShip.x + SPACESHIP_WIDTH &&
            bullet.y + bullet.height >= redShip.y &&
            bullet.y <= redShip.y + SPACESHIP_HEIGHT) {
            redHealth--;
            redFlash = 12;
            createHitEffect(redShip.x + SPACESHIP_WIDTH / 2, redShip.y + SPACESHIP_HEIGHT / 2, RED);
            yellowBullets.splice(i, 1);
        } else if (bullet.x > WIDTH) {
            yellowBullets.splice(i, 1);
        }
    });

    redBullets.forEach((bullet, i) => {
        bullet.x -= BULLETS_VEL;
        if (bullet.x + bullet.width >= yellowShip.x &&
            bullet.x <= yellowShip.x + SPACESHIP_WIDTH &&
            bullet.y + bullet.height >= yellowShip.y &&
            bullet.y <= yellowShip.y + SPACESHIP_HEIGHT) {
            yellowHealth--;
            yellowFlash = 12;
            createHitEffect(yellowShip.x + SPACESHIP_WIDTH / 2, yellowShip.y + SPACESHIP_HEIGHT / 2, YELLOW);
            redBullets.splice(i, 1);
        } else if (bullet.x < 0) {
            redBullets.splice(i, 1);
        }
    });

    if (redHealth <= 0) {
        createVictoryExplosion(redShip.x + SPACESHIP_WIDTH / 2, redShip.y + SPACESHIP_HEIGHT / 2, RED);
        gameState = 'game-over';
    } else if (yellowHealth <= 0) {
        createVictoryExplosion(yellowShip.x + SPACESHIP_WIDTH / 2, yellowShip.y + SPACESHIP_HEIGHT / 2, YELLOW);
        gameState = 'game-over';
    }
}

function gameLoop() {
    gameTime += 0.1;

    if (screenShake > 0.5) {
        const shakeX = (Math.random() - 0.5) * screenShake;
        const shakeY = (Math.random() - 0.5) * screenShake;
        ctx.save();
        ctx.translate(shakeX, shakeY);
        screenShake *= 0.85;
    }

    if (gameState === 'control-select') {
        drawControlSelectScreen();
    } else if (gameState === 'start') {
        drawStartScreen();
    } else if (gameState === 'playing') {
        updateGameplay();
        drawGameplay();
    } else if (gameState === 'game-over') {
        const winnerText = redHealth <= 0 ? 'YELLOW WINS!' : 'RED WINS!';
        const winnerColor = redHealth <= 0 ? YELLOW : RED;
        drawWinner(winnerText, winnerColor);
    }

    if (screenShake > 0.5) {
        ctx.restore();
    }

    requestAnimationFrame(gameLoop);
}

document.addEventListener('keydown', (e) => {
    keys[e.code] = true;

    if (gameState === 'control-select') {
        if (e.code === 'Digit1') {
            controlScheme = 1;
            gameState = 'start';
        } else if (e.code === 'Digit2') {
            controlScheme = 2;
            gameState = 'start';
        }
    } else if (gameState === 'start') {
        if (e.code === 'Space') {
            resetGame();
            gameState = 'playing';
        } else if (e.code === 'KeyC') {
            gameState = 'control-select';
        }
    } else if (gameState === 'playing') {
        if (e.code === 'ControlLeft' && yellowBullets.length < MAX_BULLETS) {
            yellowBullets.push({
                x: yellowShip.x + SPACESHIP_WIDTH,
                y: yellowShip.y + SPACESHIP_HEIGHT / 2 - 3,
                width: 14,
                height: 7
            });
        }
        if (controlScheme === 1 && e.code === 'ControlRight' && redBullets.length < MAX_BULLETS) {
            redBullets.push({
                x: redShip.x - 14,
                y: redShip.y + SPACESHIP_HEIGHT / 2 - 3,
                width: 14,
                height: 7
            });
        }
    } else if (gameState === 'game-over') {
        if (e.code === 'KeyR') {
            resetGame();
            gameState = 'playing';
        } else if (e.code === 'Escape') {
            gameState = 'start';
        }
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.code] = false;
});

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
});

canvas.addEventListener('mousedown', (e) => {
    mouseDown = true;
    if (gameState === 'playing' && controlScheme === 2 && redBullets.length < MAX_BULLETS) {
        redBullets.push({
            x: redShip.x - 14,
            y: redShip.y + SPACESHIP_HEIGHT / 2 - 3,
            width: 14,
            height: 7
        });
    }
});

canvas.addEventListener('mouseup', () => {
    mouseDown = false;
});

initStars();
initShootingStars();
initNebula();
gameLoop();
