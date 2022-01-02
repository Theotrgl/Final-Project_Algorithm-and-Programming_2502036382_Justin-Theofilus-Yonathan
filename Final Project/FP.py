#Import Modules and Level data
import pygame
from pygame.locals import *
from pygame import mixer
from levels import level_1, level_2, level_3

#Initializing modules
pygame.mixer.pre_init(42100,-16,2,512)
mixer.init()
pygame.init()


clock=pygame.time.Clock()
fps=60
screen_width=700
screen_height=400
screen=pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Man Vs Slime")

#Fonts and Colors
font_text=pygame.font.SysFont("Termaoma",22)
Yellow=(255,255,51)

#World Variables
tile_size=50
game_over=0
main_menu=True
end=False



#Images
bg_img= pygame.image.load('Img/bg.jpg')
restart_img=pygame.image.load("Img/restart.png")
restart_img=pygame.transform.scale(restart_img,(120,50))
start_img=pygame.image.load('Img/start.png')
start_img=pygame.transform.scale(start_img,(200,100))
arrow=pygame.image.load('Img/arrow.png')
arrow=pygame.transform.scale(arrow,(30,40))
GameOver=pygame.image.load("Img/Game_over.png")
replay_img=pygame.image.load("Img/replay.png")
replay_img=pygame.transform.scale(replay_img,(120,50))
thankyou=pygame.image.load("Img/thanks.png")
thankyou=pygame.transform.scale(thankyou,(300,200))
Title=pygame.image.load("Img/Title.png")
Title=pygame.transform.scale(Title,(600,200))

#Sounds
pygame.mixer.music.load("SFX/menu.mp3")
pygame.mixer.music.play(-1,0.0,5000)
Jump=pygame.mixer.Sound("SFX/jump.wav")
Jump.set_volume(0.2)
Death=pygame.mixer.Sound("SFX/death.wav")
Win=pygame.mixer.Sound("SFX/win.wav")
Win.set_volume(0.2)
Transition=pygame.mixer.Sound("SFX/transition.wav")
Transition.set_volume(0.2)

#Functions
#Function to add Text
def draw_text(text,font,color,x,y):
    img=font.render(text,True,color)
    screen.blit(img,(x,y))

#Function to reset levels(Emptying world data stored previously)
def reset_level():
    player.reset(0,screen_height - 100)
    enemy_group.empty()
    gate_group.empty()
    gate1_group.empty()
    gate2_group.empty()
    
    #For changing and restarting levels
    if game_over==1:
        World_data=level_2
    if game_over==2:
        World_data=level_3
    if game_over==3:
        World_data=level_1
    
        
    
    
    
    world=World(World_data)
    return world
        


#Classes
#Button Class to make buttons(taking mouse point input and confirming click using pygame functions)
class Button():
    def __init__(self,x,y,image):
        self.image= image
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.clicked=False
    #To draw buttons onto game screen
    def draw(self):
        action=False
        pos=pygame.mouse.get_pos()
        #Setting collision points between mouse cursor and button area
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]==True and self.clicked==False:
                action=True
                self.clicked=True

        if pygame.mouse.get_pressed()[0]==False:
            self.clicked=False
        screen.blit(self.image,self.rect)
        return action


        

    


#Player Class
#Defining what player is capable of doing(Setting jump height, adding gravity, movement speed,etc.)
class Player():
    def __init__(self,x,y):
        self.reset(x,y)
    
    def update(self,game_over):
        dx=0
        dy=0
        walk_cooldown=10
        if game_over==0:
            #Adding keypresses for movement using pygame function
            key=pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped==False and self.in_air==False:
                Jump.play()
                self.vel_y = -12
                self.jumped=True
            if key[pygame.K_SPACE]==False:
                self.jumped=False
            if key[pygame.K_a]:
                dx -= 2
                self.direction=-1
                self.counter+=1
            if key[pygame.K_d]:
                dx += 2
                self.direction=1
                self.counter+=1
            if key[pygame.K_d]==False and key[pygame.K_a]==False:
                self.counter=0
                self.index=0
                if self.direction==1:
                    self.image=self.images_right[self.index]
                if self.direction== -1:
                    self.image=self.images_left[self.index]
            
                

            #Animation Process
            if self.counter > walk_cooldown:
                self.counter=0
                self.index+=1
                if self.index>= len(self.images_right):
                    self.index=0
                if self.direction==1:
                    self.image=self.images_right[self.index]
                if self.direction== -1:
                    self.image=self.images_left[self.index]
                
            #Adding Gravity and setting jump height            
            self.vel_y+=1
            if self.vel_y>20:
                self.vel_y=20
            dy+=self.vel_y
            self.in_air=True
            #Adding collision for blocks in world data
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                    dx=0
                if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                    if self.vel_y<0:
                        dy=tile[1].bottom-self.rect.top
                        self.vel_y=0
                    elif self.vel_y>=0:
                        dy=tile[1].top-self.rect.bottom
                        self.vel_y=0
                        self.in_air=False
            

            #Adding collision for other entities(Enemies and gates)
            if pygame.sprite.spritecollide(self,enemy_group,False):
                game_over=-1
                Death.play()
            if pygame.sprite.spritecollide(self,gate_group,False):
                game_over=1 
                Transition.play()
            if pygame.sprite.spritecollide(self,gate1_group,False):
                game_over=2
                Transition.play()
            if pygame.sprite.spritecollide(self,gate2_group,False):
                game_over=3
                Win.play()

            self.rect.x += dx
            self.rect.y += dy
        #Death Animation
        elif game_over==-1:
            self.image=self.dead_image
            self.rect.y-=2


        screen.blit(self.image,self.rect)
        return game_over
    #For reseting player after change of levels
    def reset(self,x,y):
        self.images_right=[]
        self.images_left=[]
        self.index=0
        self.counter=0
        #Adding walk animation keyframes into lists which is itterated and drawn onto screen in the main game loop
        for num in range(1,5):
            img_right=pygame.image.load(f'Img/charaR{num}.1.png')
            img_right=pygame.transform.scale(img_right,(30,40))
            img_left=pygame.transform.flip(img_right,True,False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image=self.images_right[self.index]
        self.rect=self.image.get_rect()
        self.dead_image=pygame.image.load('Img/dead.png')
        self.dead_image=pygame.transform.scale(self.dead_image,(30,40)) 
        self.rect.x=x
        self.rect.y=y
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.vel_y=0
        self.jumped=False
        self.direction=0
        self.in_air=True
        
#World Class
class World():
    def __init__(self,data):
        self.tile_list=[]

        #Images for World assets
        floor_img= pygame.image.load('Img/pixel-platformer-blocks/Tiles/Sand/tile_0025.png')
        floor2_img= pygame.image.load("Img/pixel-platformer-blocks/Tiles/Rock/tile_0006.png")
        floor3_img= pygame.image.load("Img/pixel-platformer-blocks/Tiles/Marble/tile_0015.png")

        row_counter=0
        #Using counters to turn level data list which are numbers to correspond with a certain image
        for row in data:
            column_counter=0
            for tile in row:
                if tile==1:
                    img=pygame.transform.scale(floor_img,(tile_size,tile_size))
                    img_rect=img.get_rect()
                    img_rect.x=column_counter*tile_size
                    img_rect.y=row_counter*tile_size
                    tile=(img,img_rect)
                    self.tile_list.append(tile)
                if tile==2:
                    img=pygame.transform.scale(floor_img,(tile_size/2,tile_size/2))
                    img_rect=img.get_rect()
                    img_rect.x=column_counter*tile_size
                    img_rect.y=row_counter*tile_size
                    tile=(img,img_rect)
                    self.tile_list.append(tile)
                if tile==3:
                    slime= Enemy(column_counter*tile_size,row_counter*tile_size-3)
                    enemy_group.add(slime)
                if tile==4:
                    img=pygame.transform.scale(floor_img,(tile_size/2,tile_size))
                    img_rect=img.get_rect()
                    img_rect.x=column_counter*tile_size-(tile_size/2)
                    img_rect.y=row_counter*tile_size
                    tile=(img,img_rect)
                    self.tile_list.append(tile)
                if tile==5:
                    gate= Gate(column_counter*tile_size,row_counter*tile_size)
                    gate_group.add(gate)
                if tile==6:
                    gate1= Gate(column_counter*tile_size,row_counter*tile_size)
                    gate1_group.add(gate1)
                if tile==7:
                    gate2= Gate(column_counter*tile_size,row_counter*tile_size)
                    gate2_group.add(gate2)
                if tile==8:
                    img=pygame.transform.scale(floor2_img,(tile_size,tile_size))
                    img_rect=img.get_rect()
                    img_rect.x=column_counter*tile_size
                    img_rect.y=row_counter*tile_size
                    tile=(img,img_rect)
                    self.tile_list.append(tile)
                if tile==9:
                    img=pygame.transform.scale(floor2_img,(tile_size/2,tile_size/2))
                    img_rect=img.get_rect()
                    img_rect.x=column_counter*tile_size
                    img_rect.y=row_counter*tile_size
                    tile=(img,img_rect)
                    self.tile_list.append(tile)
                if tile==-1:
                    img=pygame.transform.scale(floor3_img,(tile_size,tile_size))
                    img_rect=img.get_rect()
                    img_rect.x=column_counter*tile_size
                    img_rect.y=row_counter*tile_size
                    tile=(img,img_rect)
                    self.tile_list.append(tile)
                if tile==-2:
                    img=pygame.transform.scale(floor3_img,(tile_size/2,tile_size/2))
                    img_rect=img.get_rect()
                    img_rect.x=column_counter*tile_size
                    img_rect.y=row_counter*tile_size
                    tile=(img,img_rect)
                    self.tile_list.append(tile)
                
                column_counter+=1
            row_counter+=1
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0],tile[1])
            
#Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("Img/E1.1.png")
        self.image=pygame.transform.scale(self.image,(30,20))
        self.rect=self.image.get_rect()
        self.rect.x=x 
        self.rect.y=y+32
        self.move_direction=1
        self.move_counter=0
    def update(self):
        self.rect.x+=self.move_direction
        self.move_counter+=0.9
        if abs(self.move_counter)>70:
            self.move_direction*=-1
            self.move_counter*=-1
#Gate Classes
class Gate(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("Img/Gate.png")
        self.image=pygame.transform.scale(self.image,(tile_size,int(tile_size*1.5)))
        self.rect=self.image.get_rect()
        self.rect.x=x 
        self.rect.y=y-tile_size//2+3
class Gate1(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("Img/Gate.png")
        self.image=pygame.transform.scale(self.image,(tile_size,int(tile_size*1.5)))
        self.rect=self.image.get_rect()
        self.rect.x=x 
        self.rect.y=y-tile_size//2+3
class Gate2(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("Img/Gate.png")
        self.image=pygame.transform.scale(self.image,(tile_size,int(tile_size*1.5)))
        self.rect=self.image.get_rect()
        self.rect.x=x 
        self.rect.y=y-tile_size//2+3
        
        



#Setting Initial game level after main menu
World_data=level_1
#Setting up properties and position of sprites and buttons
player=Player(0,screen_height - 90)
#Adding sprites into groups
enemy_group=pygame.sprite.Group()
gate_group=pygame.sprite.Group()
gate1_group=pygame.sprite.Group()
gate2_group=pygame.sprite.Group()
replay_button=Button(screen_width//2-65,screen_height//2+80,replay_img)
start_button=Button(screen_width//2-110,screen_height//2+60,start_img)
restart_button=Button(screen_width//2-60,screen_height//2+50,restart_img)

world=World(World_data)


#Main Line of Code
run = True
while run==True:

    clock.tick(fps)
    #Blit=Fuction to draw images onto game screen
    screen.blit(bg_img,(0,0))
    #Transform.scale()=Fumction to scale an image to desired ratios
    pygame.transform.scale(bg_img,(700,500))
    #Creating main menu conditions outside of main game code so that the world data doesnt pop up and we only get the bg image
    if main_menu==True:
        screen.blit(Title,(screen_width//2-300,screen_height//2-160))
        #Displaying button to main menu screen
        if start_button.draw():
            main_menu=False

    else:
        #Displaying world data elements to screen
        world.draw()
        enemy_group.update()
        enemy_group.draw(screen)
        gate_group.draw(screen)
        gate1_group.draw(screen)
        gate2_group.draw(screen)
        game_over=player.update(game_over)
        #Actions done on death
        if game_over==-1:
            if replay_button.draw()==True:
                player.reset(0,screen_height - 100)
                game_over=0
            screen.blit(GameOver,(screen_width//2-270,screen_height//2-150))
        #Actions done when completing all 3 levels
        if game_over==3:
            if restart_button.draw()==True:
                World_data=[]
                world=reset_level()
                game_over=0
            screen.blit(thankyou,(screen_width//2-150,screen_height//2-160))

        #Adding texts to show end goal to player
        if World_data==level_1:
            draw_text("Enter Here!",font_text,Yellow,615,250)
            screen.blit(arrow,(615,270))
        
        

    
        #Code to reset levels and world data so that the blocks wont stack on top of each other
        if game_over==1:
            World_data=[]
            world=reset_level()
            game_over=0
        if game_over==2:
            World_data=[]
            world=reset_level()
            game_over=0
        

        
        

    #To enable closing the game window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    #To enable screen refresh so that everything will be visible
    pygame.display.update()

pygame.quit()