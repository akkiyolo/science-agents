export default class Character {
  constructor(scene, config) {
    this.scene = scene;
    this.id = config.id;
    this.name = config.name;
    this.spawnPoint = config.spawnPoint || { x: 500, y: 500 }; 
    this.spriteKey = config.spriteKey;
    
    this.isRoaming = config.canRoam !== false; 
    this.moveSpeed = config.moveSpeed || 40;
    this.movementTimer = null;
    this.currentDirection = null;
    this.moveDuration = 0;
    this.pauseDuration = 0;
    this.roamRadius = config.roamRadius || 200; 

    // Create the sprite from the static image
    this.sprite = this.scene.physics.add
      .sprite(this.spawnPoint.x, this.spawnPoint.y, this.spriteKey)
      .setImmovable(true);
      
    // Set a smaller size and adjust collision box
    if (this.sprite.texture && this.sprite.texture.getSourceImage()) {
        const texWidth = this.sprite.texture.getSourceImage().width;
        const texHeight = this.sprite.texture.getSourceImage().height;
        this.sprite.setSize(texWidth * 0.5, texHeight * 0.4);
        this.sprite.setOffset(texWidth * 0.25, texHeight * 0.6);
    }
    
    this.sprite.setScale(0.5); // Scale down the AI generated images

    this.originX = this.spawnPoint.x;
    this.originY = this.spawnPoint.y;

    if (config.worldLayer) {
        this.scene.physics.add.collider(this.sprite, config.worldLayer);
    }
    
    this.createNameLabel();
    
    if (this.isRoaming) {
      this.startRoaming();
    }
  }
  
  facePlayer(player) {
    const dx = player.x - this.sprite.x;
    const dy = player.y - this.sprite.y;
    
    if (Math.abs(dx) > Math.abs(dy)) {
        this.sprite.setFlipX(dx < 0);
    }
  }
  
  distanceToPlayer(player) {
    return Phaser.Math.Distance.Between(
      player.x, player.y,
      this.sprite.x, this.sprite.y
    );
  }
  
  isPlayerNearby(player, distance = 70) {
    return this.distanceToPlayer(player) < distance;
  }
  
  startRoaming() {
    this.chooseNewDirection();
  }
  
  chooseNewDirection() {
    if (this.movementTimer) {
      this.scene.time.removeEvent(this.movementTimer);
    }
    
    if (Math.random() < 0.6) { 
      const directions = ['left', 'right', 'up', 'down'];
      this.currentDirection = directions[Math.floor(Math.random() * directions.length)];
      
      if (this.currentDirection === 'left') this.sprite.setFlipX(true);
      if (this.currentDirection === 'right') this.sprite.setFlipX(false);
      
      this.moveDuration = Phaser.Math.Between(500, 1500);
      this.movementTimer = this.scene.time.delayedCall(this.moveDuration, () => {
        this.sprite.body.setVelocity(0);
        this.chooseNewDirection();
      });
    } else {
      this.currentDirection = null;
      this.pauseDuration = Phaser.Math.Between(1000, 3000);
      this.movementTimer = this.scene.time.delayedCall(this.pauseDuration, () => {
        this.chooseNewDirection();
      });
    }
  }
  
  moveInCurrentDirection() {
    if (!this.currentDirection) return;
    
    this.sprite.body.setVelocity(0, 0); 
    
    switch(this.currentDirection) {
      case 'left':
        this.sprite.body.setVelocityX(-this.moveSpeed);
        break;
      case 'right':
        this.sprite.body.setVelocityX(this.moveSpeed);
        break;
      case 'up':
        this.sprite.body.setVelocityY(-this.moveSpeed);
        break;
      case 'down':
        this.sprite.body.setVelocityY(this.moveSpeed);
        break;
    }
    
    const distanceFromSpawn = Phaser.Math.Distance.Between(
      this.sprite.x, this.sprite.y,
      this.originX, this.originY
    );
    
    if (distanceFromSpawn > this.roamRadius) {
      this.sprite.body.setVelocity(0);
      const dx = this.originX - this.sprite.x;
      const dy = this.originY - this.sprite.y;
      
      if (Math.abs(dx) > Math.abs(dy)) {
        this.currentDirection = dx > 0 ? 'right' : 'left';
        this.sprite.setFlipX(this.currentDirection === 'left');
      } else {
        this.currentDirection = dy > 0 ? 'down' : 'up';
      }
      
      if (this.movementTimer) {
        this.scene.time.removeEvent(this.movementTimer);
      }
      
      this.movementTimer = this.scene.time.delayedCall(1000, () => {
        this.chooseNewDirection();
      });
    }
  }
  
  update(player, isInDialogue) {
    if (isInDialogue && this.isPlayerNearby(player, 100)) {
      this.sprite.body.setVelocity(0);
      this.facePlayer(player);
      
      if (this.movementTimer) {
        this.scene.time.removeEvent(this.movementTimer);
        this.movementTimer = null;
      }
    } 
    else if (this.isPlayerNearby(player, 60)) {
      this.sprite.body.setVelocity(0);
      this.facePlayer(player);
      
      if (this.movementTimer) {
        this.scene.time.removeEvent(this.movementTimer);
        this.movementTimer = null;
      }
    } 
    else if (this.isRoaming) {
      if (!this.movementTimer) {
        this.startRoaming();
      }
      this.moveInCurrentDirection();
    } else {
      this.sprite.body.setVelocity(0);
    }
    
    this.updateNameLabelPosition();
  }

  createNameLabel() {
    this.nameLabel = this.scene.add.text(0, 0, this.name, {
      font: "bold 12px Arial",
      fill: "#ffffff",
      stroke: "#000000",
      strokeThickness: 3,
      padding: { x: 4, y: 2 },
      align: "center"
    });
    this.nameLabel.setOrigin(0.5, 1);
    this.nameLabel.setDepth(20);
    this.updateNameLabelPosition();
  }

  updateNameLabelPosition() {
    if (this.nameLabel && this.sprite) {
      this.nameLabel.setPosition(
        this.sprite.x,
        this.sprite.y - (this.sprite.displayHeight / 2) - 5
      );
    }
  }
}
