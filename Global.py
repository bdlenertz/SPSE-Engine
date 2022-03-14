import pygame
import os
import math
import pickle
from enum import Enum

pygame.font.init()
pygame.init()

#Image Variables
PixelSize = 3 #How many game pixel per pixels, Scales the image by PixelSize
ImageWidth = 18 * 8 * PixelSize
ImageHeight = 32 * 8 * PixelSize
GameName = "Temp"

#Base Folder
BaseProjectFolder = os.path.dirname(__file__)

#Game Loop
GameLoop = True
Clock = pygame.time.Clock()
MaxFps = 30

#Visual
PictureFolder = os.path.join(BaseProjectFolder, "Tiles")
FontFolder = os.path.join(BaseProjectFolder, "Font")
#Draw Surface
DrawSurface = pygame.Surface((ImageWidth / PixelSize, ImageHeight / PixelSize))
Win = pygame.display.set_mode((ImageWidth, ImageHeight))
pygame.display.set_caption(GameName)

#
#   VISUAL
#

#Image/ Color
class Color(Enum):
    TransparentColor = (135,209,122)
    BackGroundColor = (204, 0, 36)

def LoadAlphaImage(ImageName, Folder = PictureFolder):
    return pygame.image.load(os.path.join(Folder, ImageName + ".PNG"))

def LoadImage(ImageName):
    return LoadAlphaImage(ImageName).convert()

def LoadTransparentImage(ImageName, Folder = PictureFolder):
    temp = LoadAlphaImage(ImageName, Folder)
    temp.set_colorkey(Color.TransparentColor.value)
    return temp.convert()

class ImageManager(Enum):
    #Stores all of the images
    NotImplemented
    DebugImage = LoadImage("DebugImage")
    #OpaqueImage = LoadImage("OpaqueImage")
    #TransparentImage = LoadTransparentImage("TransparentImage")
    #AlphaImage = LoadAlphaImage("AlphaImage")

#Font
class FontTemplate():
    def __init__(self, FontFolderName, StartingIndex, EndingIndex, DistanceBetweenRows, DistanceBetweenChars):
        FolderFile = os.path.join(FontFolder, FontFolderName)
     
        self.FontImages = []
        for i in range(StartingIndex, EndingIndex, 1):
            self.FontImages.append(LoadTransparentImage(str(i), FolderFile))
        self.FontImages = tuple(self.FontImages)

        self.StartingIndex = StartingIndex
        self.DistanceBetweenRows = 6 + DistanceBetweenRows
        self.WorstCaseDigitSize = (6, 6 + DistanceBetweenRows)

    def ReturnFontImage(self, Char):
        return self.FontImages[ord(Char) - self.StartingIndex]

class Fonts(Enum):
    Default = FontTemplate("Default", 32, 123, 3, 1)
    
class Font():

    BreakChars = (" ", ".", ",")    #Chars that breaks the string and skips to a new line
    MaximumSearchBack = 10   #Maximum Number of chrs it can search back, before giving up and forcing a new line

    def GetFontImage(FontEnum, String, FontImageWidth, Centered = False):
        #Get Font Image
        ThisFont = FontEnum.value
        #Gets a rough size of the surface to draw on, worst case it can fit the string, but can be trimmed
        HorizontalSpaceNeeded = len(String) * ThisFont.WorstCaseDigitSize[0]
        RowsNeeded = math.ceil(HorizontalSpaceNeeded / FontImageWidth * 1.3) #Multiplys by 1.3 to make up for any space lost by cutting space
        if (RowsNeeded == 1):
            #Can fit in a single row
            Return = pygame.Surface((HorizontalSpaceNeeded,  ThisFont.WorstCaseDigitSize[1] - 1))            
        else:
            #Can only fit in multiple rows
            Return = pygame.Surface((FontImageWidth, ThisFont.WorstCaseDigitSize[1] * RowsNeeded - 1))
        #Goes through each row and prints the char
        Offset = [0,0]
        MaximumXValue = -1
        #Variables regarding the strings
        SpriteList = []
        Index = 0
        #CharSizes
        RowSize = ThisFont.WorstCaseDigitSize[1]

        def PrintLine(spriteList):
            #Prints the TextLine and Resets the Sprite List
            if (Centered):
                PixelLength = 0
                for Sprite in spriteList:
                    PixelLength += Sprite.get_width()
                Offset[0] = (FontImageWidth - PixelLength) // 2
            else:
                Offset[0] = 0
            #Prints a line, and sets the MaximumXValue
            for Sprite in spriteList:
                #Goes through each sprite and prints it
                Return.blit(Sprite, Offset)
                Offset[0] += Sprite.get_width()
            #Sets the Maximum X Value, and sets the Sprite List back to 0
            return max(Offset[0], MaximumXValue), []

        def SkipLine(index):
            currentSprite = ThisFont.ReturnFontImage(String[index])
            Offset[0] = currentSprite.get_width()
            Offset[1] += RowSize
            return currentSprite

        def FindBreakPoint():
            EndingIndex = max(Index - Font.MaximumSearchBack,0)
            WhileIndex = Index - 1
            while (WhileIndex >= EndingIndex):
                Char = String[WhileIndex]
                for Key in Font.BreakChars:
                    if (Key == Char):
                        return (Index - 1) - WhileIndex
                
                WhileIndex -= 1
            return 0

        def RowBreak(LineBreak):
            spriteList = SpriteList
            index = Index

            for i in range(FindBreakPoint()):
                del spriteList[-1]
                index = index - 1
            
            maximumXValue, spriteList = PrintLine(spriteList)

            if (LineBreak):
                #Skips the asterisk
                index += 1
                
            currentSprite = SkipLine(index)
            return maximumXValue, spriteList, currentSprite, index     

        while(Index < len(String)):
            CurrentChar = String[Index]
            CurrentSprite = ThisFont.ReturnFontImage(CurrentChar)
            Offset[0] += CurrentSprite.get_width()

            LineBreak = CurrentChar == '*'
            if (Offset[0] > FontImageWidth or LineBreak):
                Offset[0] -= CurrentSprite.get_width()
                MaximumXValue, SpriteList, CurrentSprite, Index = RowBreak(LineBreak) #Breaks Line

            #Adds sprite to sprite list
            SpriteList.append(CurrentSprite)
            #Increments the index
            Index += 1

        MaximumXValue,SpriteList = PrintLine(SpriteList)

        CroppedReturn = Return.subsurface((0, 0, MaximumXValue - 1, Offset[1] - RowSize - 1))
        CroppedReturn.set_colorkey((0,0,0))
        return CroppedReturn

    def CenterFontImage(FontEnum, String, FontImageWidth):
        NotImplemented 

#Tile
class RawTile(pygame.sprite.Sprite):
    def __init__(self, Pos, Image, Layer):
        pygame.sprite.Sprite.__init__(self)
        self.image = Image
        self.rect = self.image.get_rect()
        self.rect.topleft = Pos
        self.Layer = Layer
        Layers.AddToLayer(self, Layer)
        
    def Remove(self):
        Layers.RemoveFromLayer(self, self.Layer)
    
class Tile(RawTile):
    def __init__(self, Pos, ImageEnum, Layer):
        RawTile.__init__(self, Pos, ImageEnum.value, Layer)
        
#Layers
class GroupLayer():
    #Holds Layers of sprites, buttons
    def __init__(self):
        self.NumberOfLayers = 0
        self.Layers = []

    def AddToLayer(self, Object, Layer, EmptyObject, Child = None):
        if (self.NumberOfLayers <= Layer):
            #Needs to add more sprite layers in order to fit the new tile
            Difference = Layer - self.NumberOfLayers + 1
            #Find the number of tiles that need to be added
            if (Difference >= 3):
                #DEBUG, raises an warning that may be wasting layers, can be ignored
                print("Added " + Difference + " layers for a single tile")
                    
            for i in range(Difference):
                #Adds layers
                self.NumberOfLayers += 1
                self.Layers.append(EmptyObject)

                if (Child):
                    Child.LayerAdded()

        self.Layers[Layer].add(Object)

    def RemoveFromLayer(self, Object, Layer):
        CurrentLayer = self.Layers[Layer]
        if (len(CurrentLayer) == 0):
            #DEBUG, There are no sprites in the Layer
            print("Trying to remove a sprite from a layer that is empty")
            Error

        try:
            #Removes the Sprite
            CurrentLayer.remove(Tile)

            if (len(CurrentLayer) == 0 and Layer + 1 == self.NumberOfLayers):
                #Its the last layer and is now empty, so its going to be removed
                self.NumberOfLayers -= 1
                del self.Layers[Layer]
                
        except:
            #DEBUG, if the sprite does not exist in the layer
            print("Tryed to remove a sprite from a layer, that the tile does not exist in")
            Error

class SpriteLayer(GroupLayer):
    StartingIndex = 0
    BackGroundFill = True
        
    def __init__(self):
        GroupLayer.__init__(self)

    def AddToLayer(self, Object, Layer):
        GroupLayer.AddToLayer(self, Object, Layer, pygame.sprite.Group())

    def ChangeStartingLayer(self, StartingLayer):
        SpriteLayer.BackGroundFill = StartingLayer == 0
        SpriteLayer.StartingIndex = StartingLayer
    
    def Draw(self):
        if (SpriteLayer.BackGroundFill):
            DrawSurface.fill(Color.BackGroundColor.value)
        
        for a in range(SpriteLayer.StartingIndex, self.NumberOfLayers, 1):
            self.Layers[a].draw(DrawSurface)
        

class ButtonLayer(GroupLayer):
    Active = False
    NumberOfButtons = 0
    #Starting Index, used to disable layers
    StartingLayerIndex = 0
    CheckForSingleCollision = []
    #If Left button has been pressed
    LeftButtonPressed = False
    
    def __init__(self):
        GroupLayer.__init__(self)

    def AddToLayer(self, Object, Layer):
        GroupLayer.AddToLayer(self, Object, Layer, ())
        ButtonLayer.NumberOfButtons += 1

    def LayerAdded(self):
        #Layer added
        ButtonLayer.CheckForSingleCollision.append(None)

    def RemoveFromLayer(self, Object, Layer):
        GroupLayer.RemoveFromLayer(self, Object, Layer)
        ButtonLayer.NumberOfButtons -= 1
        if (ButtonLayer.NumberOfButtons == 0):
            ButtonLayer.Active= False

    def ButtonPressed():
        ButtonLayer.LeftButtonPressed = True

    def UpdateButton(self):
        if (ButtonLayer.Active):
            
            HousePosition = pygame.mouse.get_pos()  #Gets the position of the mouse
            HousePosition = (HousePosition[0] // PixelSize, HousePosition[1] // PixelSize)

            for i in range(ButtonLayer.StartingLayerIndex, self.NumberOfLayers, 1):
                
                if (CurrentCollision == None):
                    #Has not found a current collision
                    for Sprite in ButtonLayer:
                        #Goes through each Sprite, and checks if any of them has collided
                        CurrentCollision = Sprite.CheckForCollision(HousePosition, CurrentCollision)

                else:
                    #Already found a collision, just needs to see if it is still colliding
                    CurrentCollision =  CurrentCollision.CheckForCollisionEnd(HousePosition)         
                    if (ButtonLayer.LeftButtonPressed):
                        #Left button is pressed
                        CurrentCollision.LeftButtonPressed()
                        ButtonLayer.LeftButtonPressed = False                                  
        
class Layers():

    SpriteLayers = SpriteLayer()

    ButtonLayers = ButtonLayer()

    def AddToButtonLayer(Button, Layer):
        ButtonLayers.AddToLayer(Button, Layer)

    def RemoveFromButtonLayer(Button, Layer):
        ButtonLayers.RemoveFromLayer(Button, Layer)

    def ChangeStartingButtonLayer(StartingLayer):
        #Changes the lowest index that is tested for collision
        ButtonLayers.StartingLayerIndex = StartingLayer

    def AddToLayer(Tile, Layer):
        Layers.SpriteLayers.AddToLayer(Tile, Layer)

    def RemoveFromLayer(Tile, Layer):
        Layers.SpriteLayers.RemoveFromLayer(Tile, Layer)

    def ChangeStartingLayer(StartingLayer):
        #Changes the lowest index that is drawn, removes 
        SpriteLayers.ChangeStartingLayer(StartingLayer)

    #Left Button Pressed
    def ButtonPressed():
        ButtonLayer.ButtonPressed()

    #Update Layers
    def UpdateLayers():
        #Layers.ButtonLayers.UpdateButton()
        Layers.ButtonLayers.UpdateButton()
        Layers.DrawUpdate()

    def DrawUpdate():
        #Update each frame and draws the background
        Layers.SpriteLayers.Draw()
            
        pygame.transform.scale(DrawSurface, (ImageWidth, ImageHeight), Win)
        pygame.display.flip()

#
#Buttons
#

class SimpleButton():
    #Simple Button, Is an rectangular button, without any image, calls Hover(), StopHover(), LeftButtonClicked()
    def __init__(self, Rect, Layer, Child):
        self.Child = Child
        self.Layer = Layer
        self.Rect = Rect
        
        Layers.AddToButtonLayer(self, Layer)

    def CheckForCollision(self, Point, LastCollision):
        #If there is an collision on the button
        if (self.Rect.collidepoint(Point)):
            #The points collide
            self.Child.Hover()
            return self
        return LastCollision

    def CheckForCollisionEnd(self, Point):
        if (self.Rect.collidepoint(Point)):
            return self

        self.CallObject.StopHover()
        return None

    def LeftButtonPressed(self):
        self.Child.LeftButtonClicked()
    
    def Remove(self):
        Layer.RemoveFromButtonLayer(self, self.Layer)

class RawButton():
    #Same as button, but takes a surface instead of image manager
    def __init__(self, Pos, Image, ImageLayer, ButtonLayer, Child):
        self.Image = RawTile(Pos, Image, ImageLayer)
        self.Button = SimpleButton(Image.get_rect(), ButtonLayer, Child)

    def Remove(self):
        self.Image.Remove()
        self.Button.Remove()

class Button(RawButton):
    #Button, Has an image, and an button, with the same methods as simple button
    def __init__(self, Pos, Image, ImageLayer, ButtonLayer, Child):
        RawButton.__init__(self, Pos, Image.value, ImageLayer, ButtonLayer, Child)

class RawToggleButton(RawButton):
    #Toggle Button, has an image, and when clicked it changes to a clicked image, same methods as simple button
    def __init__(self, Pos, Image, ClickedImage, ImageLayer, ButtonLayer, Child):
        RawButton.__init__(self, Pos, Image, ImageLayer, ButtonLayer, self)

        self.DefaultImage = Image
        self.ClickedImage = ClickedImage

        self.Child = Child

        self.Clicked = False

    def ChangeImage(self, Value, Image):
        if (self.Clicked == Value):
            self.Image.image = Image
            self.Clicked = not Value

    def Hover(self):
        self.Child.Hover()

    def StopHover(self):
        self.ChangeImage(True, self.DefaultImage)
        self.Child.StopHover()

    def LeftButtonPressed(self):
        self.ChangeImage(False, self.ClickedImage)
        self.Child.LeftButtonPressed()

class ToggleButton(RawToggleButton):
    #Toggle Button, has an image, and when clicked it changes to a clicked image, same methods as simple button
    def __init__(self, Pos, Image, ClickedImage, ImageLayer, ButtonLayer, Child):
        RawToggleButton.__init__(self, Pos, Image.value, ClickedImage.value, ImageLayer, ButtonLayer, Child)

class RawHoverButton(RawButton):
    def __init__(self, Pos, Image, HoverImage, ClickedImage, ImageLayer, ButtonLayer, Child):
        RawButton.__init__(self, Pos, Image, ImageLayer, ButtonLayer, self)

        self.DefaultImage = Image
        self.HoverImage = HoverImage
        self.ClickedImage = ClickedImage

        self.Child = Child

        self.Mode = 0
        #If 0 then not selected, 1 is hover, 2 is clicked

    def ChangeImage(self, Mode, Image):
        if (self.Mode != Mode):
            self.Image.image = Image
            self.Mode = Mode

    def Hover(self):
        self.ChangeImage(1, self.HoverImage)
        self.Child.Hover()

    def StopHover(self):
        self.ChangeImage(0, self.DefaultImage)
        self.Child.StopHover()

    def LeftButtonPressed(self):
        self.ChangeImage(2, self.ClickedImage)
        self.Child.LeftButtonPressed()

class HoverButton(RawHoverButton):
    def __init__(self, Pos, Image, HoverImage, ClickedImage, ImageLayer, ButtonLayer, Child):
        RawHoverButton.__init__(Pos, Image.value, HoverImage.value, ClickedImage.value, ImageLayer, ButtonLayer, Child)

#
#Input
#

class Input():
    #Keys
    KeyCodes = [] #Stores all of the indexes on the keycode per update
    #[0] Left , [1] Right, [2] Up, [3] Down
    #Left Button Clicked
    LeftButtonClicked = False
    #Input Listener
    NumberOfGeneralInputs = 4  #Number of general inputs
    NumberOfNumberInputs = NumberOfGeneralInputs + 10  #Number of Number Inputs + GeneralInputs
    NumberOfTotalInputs = NumberOfNumberInputs + 26  #Number of Total Input, Number + General

    NumberOfInputs = NumberOfGeneralInputs #Current number of inputs
    
    InputListeners = [] #Stores all of the Input Listeners

    def AddInputListener(AudioListener, NumberInput, AlphabetInput):
        #Adds the input listener
        Input.InputListeners.append(AudioListener)
        #Checks if the NumberOfInputs need to be update, increased
        if (NumberInput):
            if (Input.NumberOfTotalInputs < Input.NumberOfNumberInputs):
                Input.NumberOfTotalInputs = Input.NumberOfNumberInputs
        elif (AlphabetInput):
            if (Input.NumberOfTotalInputs < NumberOfTotalInputs):
                Input.NumberOfTotalInputs = NumberOfTotalInputs

    def RemoveInputListener(AudioListener):
        #Remove the input listener
        Input.InputListeners.remove(AudioListener)
            
        #If there are no more inputs, then it defaults back to general input
        if (len(Input.InputListeners) == 0):
            NumberOfInputs = Input.NumberOfGeneralInputs

    def AddMouseListener(MouseListener):
        Input.InputListeners.append(MouseListener)

    def RemoveMouseListener(MouseListener):
        Input.InputListeners.remove(MouseListener)
    
    #Assign Create Keys
    def CreateKeys(KeyCodeTuple):
        #Used for loading from saved keys combinations, and for setting a default at the beginning of the game  
        for Key in KeyCodeTuple:
            Input.KeyCodes.append(Key)
        
    def AssignKeys(KeyIndex, KeyCode):
        #Assigns a key code to a certain input
        Input.KeyCodes[KeyIndex] = KeyCode
        
    def UpdateInput():
        #Turn all PressedKeys to false, Returns the GameLoop
        KeyCodes = Input.KeyCodes

        Input.LeftButtonClicked = False

        Events = pygame.event.get()
        for Event in Events:
            if Event.type == pygame.QUIT:
                return False
            elif Event.type == pygame.KEYDOWN:
                for i in range(Input.NumberOfInputs):
                    #Goes through all of the key codes, and test if the key is a key being tested for
                    if (KeyCodes[i] == Event.key):
                        #The key matches
                        for InputListener in Input.InputListeners:
                            InputListener.ButtonPressed(Event.key)
                        
            elif (Event.type == pygame.MOUSEBUTTONDOWN):
                #Called when the Mouse button was clicked
                Layers.ButtonPressed()
 
        return GameLoop

#
#   Scenes Saving
#

'''
Scene Example
OpenScene(self):  #Opens the scene, loads all of the classes that relate to the scene
CloseScene(self):  #Closes the scene, closes all of the classes that are related to it
ReturnSceneVars(self): #Returns Variables that relate to the scene, used when saving scene information
'''

class ExampleScene():
    def __init__(self):
        print("Created")

    def OpenScene(self, Arguments):
        print("Opens a scene, with arguments")

    def CloseScene(self):
        print("Closes all of the scenes")

    def UpdateScenes(self):
        print("Print Ssenes")

    def ReturnSceneVars(self):
        #Returns the Scene Variables, used when closing and reopening scenes
        return None

class StoredScene():
    def __init__(self, Scene, SceneVariables):
        self.Scene = Scene
        self.SceneVariables = SceneVariables

class SceneNames(Enum):
    Example = ExampleScene()

class Scenes():
    #Stores the current scene
    CurrentScene = None
    #Stores the scene that where visited
    StoredScenes = []
    #GlobalVariables are stored here
    ExampleVariable1 = None
    ExampleVariable2 = None

    def ChangeScene(StoredScene):
        #Changes the scene, closes the last scene and opens a new one
        if (Scenes.CurrentScene != None):
           Scenes.CurrentScene.CloseScene()

        Scenes.CurrentScene = StoredScene.Scene
        Scenes.CurrentScene.OpenScene(StoredScene.SceneVariables)
        
    def StoreOpenScene():
        #Stores the current scene, in stored scene. Does not close the scene, and stores the current scene in the first element in a tuple
        Scenes.StoredScenes.append( StoredScene(Scenes.CurrentScene, Scenes.CurrentScene.ReturnSceneVars() ))

    def OpenLastScene():
        #Opens the last scene, and closes the last one
        Scenes.ChangeScene(Scenes.StoredScenes[-1])
        del Scenes.StoredScenes[-1]

    def LoadVars(): #Is called when the game is opened and it moves all of the variables from memory to temp vars
        try:
            with open("Game.pkl","rb") as Pickle:
                SavedVars = pickle.load(Pickle)
        except:
            print("Game.pkl not found")

        #[0] is a tuple that stores the last open scene and all of the scenes that where visited before this one
        Scenes.ExampleVariable1 = SavedVars[1]
        Scenes.ExampleVariable2 = SavedVars[2]

        SavedScenes = SavedVars[0]
        Scenes.StoredScenes = list(SavedScenes[1: ])    #Saves Stored Scenes
        
        Scenes.ChangeScene(SavedScenes[0])   #Changes the Scene
        
    def SaveVars():
        #Moves the scene vars into memory, used for the when the player quits the game
        SceneTemp = [StoredScene(Scenes.CurrentScene , Scenes.CurrentScene.ReturnSceneVars()), ]
        for Scene in Scenes.StoredScenes:
            SceneTemp.append(Scene)
        SceneTemp = tuple(SceneTemp)
        
        SavedVars = (SceneTemp, Scenes.ExampleVariable1, Scenes.ExampleVariable2)

        with open("Game.pkl","wb") as Pickle:
            pickle.dump(SavedVars, Pickle)

    #Update
    def UpdateScenes():
        #Updates the Scene
        if (Scenes.CurrentScene == None):
            print("There isn't a scene open, open one you cuant")
        else:
            Scenes.CurrentScene.UpdateScene()

    #Debug
    def DebugCreateGamePkl():
        #Sets Debug Variables
        Scenes.CurrentScene = SceneNames.Example.value
        
        Scenes.SaveVars()   #Moves the new Temp Vars to memory
        print("Debug Reset Saved Var")

    #Quit game
    def CloseGame():
        Scenes.SaveVars()
        pygame.quit()
    

#Game Loop
Input.CreateKeys((pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN))
#Loads Scenes
Scenes.DebugCreateGamePkl() #Creates Pickle
Scenes.LoadVars()

while (GameLoop):

    Clock.tick(MaxFps)

    GameLoop = Input.UpdateInput()

    Layers.UpdateLayers()

Scenes.CloseGame()
