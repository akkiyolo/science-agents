import Phaser from 'phaser';
import DialogueUI from './DialogueUI';
import Character from './classes/Character';

export default class GameScene extends Phaser.Scene {
    constructor() {
        super('GameScene');
        this.player = null;
        this.cursors = null;
        this.wasd = null;
        this.scientists = [];
        this.dialogueUI = null;
        this.activeNpc = null;
        this.dialogueCooldown = false;
    }

    preload() {
        // Load Audio
        this.load.audio('bgm', 'assets/bgm.wav');

        // Load Tilesets and Map (PhiloAgents world)
        this.load.image("tuxmon-tiles", "assets/tilesets/tuxmon-sample-32px-extruded.png");
        this.load.image("greece-tiles", "assets/tilesets/ancient_greece_tileset.png");
        this.load.image("plant-tiles", "assets/tilesets/plant.png");
        this.load.tilemapTiledJSON("map", "assets/tilemaps/map.json");

        // Load Generated Sprites for the characters!
        this.load.image('player', 'assets/sprites/player.png');
        this.load.image('einstein', 'assets/sprites/einstein.png');
        this.load.image('newton', 'assets/sprites/newton.png');
        this.load.image('curie', 'assets/sprites/curie.png');
        this.load.image('galileo', 'assets/sprites/galileo.png');
        this.load.image('darwin', 'assets/sprites/darwin.png');
        this.load.image('lovelace', 'assets/sprites/lovelace.png');
        this.load.image('tesla', 'assets/sprites/tesla.png');
    }

    create() {
        // Setup Map
        const map = this.make.tilemap({ key: "map" });
        const tuxmonTileset = map.addTilesetImage("tuxmon-sample-32px-extruded", "tuxmon-tiles");
        const greeceTileset = map.addTilesetImage("ancient_greece_tileset", "greece-tiles");
        const plantTileset = map.addTilesetImage("plant", "plant-tiles");
        const tilesets = [tuxmonTileset, greeceTileset, plantTileset];

        const belowLayer = map.createLayer("Below Player", tilesets, 0, 0);
        const worldLayer = map.createLayer("World", tilesets, 0, 0);
        const aboveLayer = map.createLayer("Above Player", tilesets, 0, 0);
        
        worldLayer.setCollisionByProperty({ collides: true });
        aboveLayer.setDepth(10); // Render on top

        // Play BGM
        if (!this.sound.get('bgm')) {
            this.sound.play('bgm', { loop: true, volume: 0.1 });
        }

        // Setup Player
        const spawnPoint = map.findObject("Objects", (obj) => obj.name === "Spawn Point");
        this.player = this.physics.add.sprite(spawnPoint.x, spawnPoint.y, 'player');
        
        // Wait for texture to load to set size correctly
        this.time.delayedCall(10, () => {
            if (this.player.texture && this.player.texture.getSourceImage()) {
                const texWidth = this.player.texture.getSourceImage().width;
                const texHeight = this.player.texture.getSourceImage().height;
                this.player.setSize(texWidth * 0.5, texHeight * 0.4);
                this.player.setOffset(texWidth * 0.25, texHeight * 0.6);
            }
        });
        
        this.player.setScale(0.5);
        this.player.setCollideWorldBounds(true);
        this.physics.add.collider(this.player, worldLayer);

        // Setup Scientists using Generated AI Sprites on the Tiled Map spawn points
        const scientistConfigs = [
            { id: 'einstein', name: 'Albert Einstein', spriteKey: 'einstein', spawnName: 'Socrates' },
            { id: 'newton', name: 'Isaac Newton', spriteKey: 'newton', spawnName: 'Aristotle' },
            { id: 'curie', name: 'Marie Curie', spriteKey: 'curie', spawnName: 'Ada Lovelace' },
            { id: 'galileo', name: 'Galileo Galilei', spriteKey: 'galileo', spawnName: 'Plato' },
            { id: 'darwin', name: 'Charles Darwin', spriteKey: 'darwin', spawnName: 'Descartes' },
            { id: 'lovelace', name: 'Ada Lovelace', spriteKey: 'lovelace', spawnName: 'Leibniz' },
            { id: 'tesla', name: 'Nikola Tesla', spriteKey: 'tesla', spawnName: 'Turing' }
        ];

        this.scientists = [];
        
        scientistConfigs.forEach(config => {
            const npcSpawn = map.findObject("Objects", (obj) => obj.name === config.spawnName) || {x: 500, y: 500};
            
            const npc = new Character(this, {
                id: config.id,
                name: config.name,
                spawnPoint: npcSpawn,
                spriteKey: config.spriteKey,
                worldLayer: worldLayer,
                roamRadius: 300,
                moveSpeed: 40
            });
            
            npc.sprite.setCollideWorldBounds(true);

            // Add collision with player to open dialogue
            this.physics.add.collider(this.player, npc.sprite, () => this.handleNpcCollision(config.id));
            
            // Add collisions between scientists
            this.scientists.forEach(otherNpc => {
                this.physics.add.collider(npc.sprite, otherNpc.sprite);
            });
            
            this.scientists.push(npc);
        });

        // Input
        this.cursors = this.input.keyboard.createCursorKeys();
        this.wasd = this.input.keyboard.addKeys('W,A,S,D');
        this.input.keyboard.removeCapture('SPACE');
        
        // Camera bounds and physics
        this.cameras.main.startFollow(this.player);
        this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        
        // Zoom in dynamically to ensure the map always fills the width of the screen, removing any black bars
        const minZoom = Math.max(1.5, window.innerWidth / map.widthInPixels);
        this.cameras.main.setZoom(minZoom);
        
        this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        this.physics.world.setBoundsCollision(true, true, true, true);

        // Dialogue UI
        this.dialogueUI = new DialogueUI(this);
        
        // Escape to close dialogue (Phaser canvas level)
        this.input.keyboard.on('keydown-ESC', () => {
            this.closeDialogue();
        });
    }

    closeDialogue() {
        if (!this.dialogueUI.isVisible) return;
        
        this.dialogueUI.hide();
        this.activeNpc = null;
        
        this.dialogueCooldown = true;
        this.time.delayedCall(2000, () => {
            this.dialogueCooldown = false;
        });
    }

    handleNpcCollision(npcId) {
        if (!this.dialogueUI.isVisible && !this.dialogueCooldown) {
            this.activeNpc = npcId;
            this.dialogueUI.show(npcId);
        }
    }

    update(time, delta) {
        const isInDialogue = this.dialogueUI.isVisible;
        
        if (!isInDialogue) {
            this.updatePlayerMovement();
        } else {
            this.player.body.setVelocity(0);
        }
        
        // Depth sorting (y-sort) so sprites overlay correctly
        this.player.setDepth(this.player.y);
        
        this.scientists.forEach(npc => {
            if (npc.sprite && npc.sprite.active) {
                npc.sprite.setDepth(npc.sprite.y);
                npc.update(this.player, isInDialogue && this.activeNpc === npc.id);
            }
        });
    }

    updatePlayerMovement() {
        const speed = 175;
        this.player.body.setVelocity(0);

        if (this.cursors.left.isDown || this.wasd.A.isDown) {
            this.player.body.setVelocityX(-speed);
            this.player.setFlipX(true);
        } else if (this.cursors.right.isDown || this.wasd.D.isDown) {
            this.player.body.setVelocityX(speed);
            this.player.setFlipX(false);
        }

        if (this.cursors.up.isDown || this.wasd.W.isDown) {
            this.player.body.setVelocityY(-speed);
        } else if (this.cursors.down.isDown || this.wasd.S.isDown) {
            this.player.body.setVelocityY(speed);
        }

        this.player.body.velocity.normalize().scale(speed);
    }
}
