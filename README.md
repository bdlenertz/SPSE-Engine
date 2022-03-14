# SPSE-Engine
Simple Python engine that I am using to create games from. A lot of the elements in the engine come from previous projects that I have worked on. With the goal of the project to be barebones and as simple as possible.

==Purpose Of The Engine==
The engine was built to be a simple, well written and documented game engine, that would be used to create small scale, low res games. Unlike Unity engine with its great 3d pipeline, pygame isn't based on vector graphics so it is well suited for pixel graphics

==Goal Of The Engine==
Simple
Python
Sprite
Engine
The Engine was made to be as simple and readable as possible, inorder to make debuging as easy as possible, with the goal of having development of games focus as much as possible on the aspects of the game, and not the framework it was built upon. 
The program was written in python, bacause of the pygame library, and because I wanted a project that would be a nice break from C# and Unity Engine. 
The program is based on Tiles, Which inherits from pygames sprites. With all visual being done without the use of vector graphics, for the purpose of being used as a pixel based engine.

==Features Of The Engine==
Tiles=
Tiles are used to draw anything onto the screen, they are created with a pos, image and layer. With each frame being drawn onto the draw surface, in order of the specified layers.
Buttons=
Buttons are used very simularily to buttons in UnityEngine, with Hover(), StopHover(), LeftButtonClicked(), with the Buttons calling the child object with the events of Hover(), StopHover(), LeftButtonClicked(). Once a button is hovered over, only that button is checked for the StopHover() event. So there are Layers for when Multiple button are espected to be in "Hover" mode.
Scenes=
This is very simular to Unity Engine. With scenes being loaded and unloaded acting just like Unity Engine. Scenes store game wide varaibles, that are stored when the application closes. Each scene has a "player" object. That creates all of the Tiles and code needed for the scene, with a Destroy() that wuld removed everything on the scene. WIth a UpdateScene() being called every frame. Scenes are stored in memory and regardless when the application is closed the scene would be stored and reopened on launch. 
Fonts=
Creates An Image, given the font, string, and if it is centered, supports multiple fonts.


  
    



