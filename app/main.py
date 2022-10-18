import pygame
import os, sys
import time
import random
from fcntl import ioctl
from iotcl_cmds import *

fd = os.open("/dev/mydev", os.O_RDWR)

pygame.init()
pygame.font.init()

width, height = 1200, 900
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Jogo IHS")
pontuacao = 0
data = 0
qtdSwitches = 0
circlesPosX = 300
circlesPosY = 450
switchesPosX = 170
switchesPosY = 350
switchNumber = 0
buttonLevel = 1
switchSum = 262143
switchNumberPosX = 180 
switchNumberPosY = 570

randomTicks = []
userSwitchs = []
sevenDisplay = ["c0", "f9", "a4", "b0", "99", "92", "82", "f8", "80", "90"]

WHITE = (255, 255, 255)
GREEN = 9, 125, 30
BLACK = (0, 0, 0)
RED =  (255, 0, 0)
LIGHTBLUE = (42, 194, 245)
GRAY = 80, 80, 82
YELLOw = 247,191,64

MENU_BACKGROUND = pygame.transform.scale(pygame.image.load("menu-background.jpg"), (width, height))

def game():
    global level
    global speed
    global pontuacao
    global qtdSwitches
    speed = 0.8
    FPS = 60
    pontuacao = 0
    running = True
    clock = pygame.time.Clock()
    level = 1
    qtdSwitches = 3
    buttonLevel = 1
    gameFont = pygame.font.SysFont("comicsans", 50)

    def redraw():

        screen.fill(YELLOw)

        global randomTicks
        global level
        global pontuacao
        global speed
        global buttonLevel
        global userSwitchs
        global data
        global qtdSwitches

        levelLabel = gameFont.render("Nível : " + str(level), 1, WHITE)
        screen.blit(levelLabel, (20, 20))

        ## Dois tipos de nivel

        randomTicks = []
        userInput = []
        randomButtons = []
        switchNumber = 0
        a = 0

        # Mostrando pontuacao no display de 7 segmentos.        
        pontuacaoStr = ""

        for num in str(pontuacao):
            pontuacaoStr += sevenDisplay[int(num)]

        qtd = 4 - int(len(pontuacaoStr) / 2)
        for i in range(0, qtd):
            pontuacaoStr = sevenDisplay[0] + pontuacaoStr

        pontuacaoStr = "0x" + pontuacaoStr
        pontuacaoStr = int(pontuacaoStr, 16)

        ioctl(fd, WR_R_DISPLAY)
        retval = os.write(fd, pontuacaoStr.to_bytes(4, 'little'))

        if (level % 2 == 1):

            for i in range(0, 4):
                pygame.draw.circle(screen, WHITE, [circlesPosX + 200 * i, circlesPosY], 90, 120)

            for i in range(0, buttonLevel):
                a = random.randint(0, 3)
                randomTicks.append(a)
                randomButtons.append(15 - (2**(3 - a)))

            for rr in randomTicks:
                pygame.draw.circle(screen, GRAY, [circlesPosX + 200 * rr, circlesPosY], 90, 120)
                pygame.display.update()
                time.sleep(speed)
                pygame.draw.circle(screen, WHITE, [circlesPosX + 200 * rr, circlesPosY], 90, 120)
                pygame.display.update()
                time.sleep(speed)

            while len(userInput) < buttonLevel:
                ioctl(fd, RD_PBUTTONS)
                data = os.read(fd, 4)
                data = int.from_bytes(data, 'little')
                time.sleep(0.4)

                while data == 15:
                    ioctl(fd, RD_PBUTTONS)
                    data = os.read(fd, 4)
                    data = int.from_bytes(data, 'little')
                    time.sleep(0.4)
                userInput.append(data)                

            if (randomButtons == userInput):
                screen.fill(YELLOw)
                winFont = pygame.font.SysFont("comicsans", 150)
                levelWinLabel = winFont.render("Venceu!!!", 1, GREEN)
                screen.blit(levelWinLabel, (370, 300))
                levelWinClick = gameFont.render("Clique em algum botão para avançar para o próximo nível", 1, GREEN)
                screen.blit(levelWinClick, (130, 550))
                buttonClick = gameFont.render("Clique em algum botao para avançar", 1, GREEN)
                screen.blit(buttonClick, (270, 600))
                pygame.display.update()
                
                pontuacao += 10 * level 
                if pontuacao > 9999:
                    pontuacao = 9999

                speed -= 0.02
                # Se acertou, ligar os leds verdes e apagar os leds vermelhos.
                data = 0x0
                ioctl(fd, WR_RED_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))
                data = 0xFFFFFFFF
                ioctl(fd, WR_GREEN_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))
                time.sleep(3)
                # Depois disso, desligar os leds verdes.
                data = 0X0
                ioctl(fd, WR_GREEN_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))

                data = 15
                while data == 15:
                    ioctl(fd, RD_PBUTTONS)
                    data = os.read(fd, 4)
                    data = int.from_bytes(data, 'little')

            else:
                levelLoseLabel = gameFont.render("Perdeu", 1, RED)
                screen.blit(levelLoseLabel, (550, 300))
                pygame.display.update()
                #se errou ligar todos os leds vermelhos e apagar todos os leds verdes.
                data = 0xFFFFFFFF
                ioctl(fd, WR_RED_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))
                data = 0x0
                ioctl(fd, WR_GREEN_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))
                time.sleep(3)
                # Desligar os leds vermelhos
                data = 0x0
                ioctl(fd, WR_RED_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))

                lose()
        else:

            correctSwitchSum = switchSum
            inputSwitchSum = switchSum

            for i in range(0, 18):
                pygame.draw.rect(screen, WHITE, pygame.Rect(switchesPosX + 50*i, switchesPosY, 40, switchesPosX+20))
                numberLabel = gameFont.render(str(switchNumber), 1, WHITE)
                screen.blit(numberLabel, (switchNumberPosX + 50 * i, switchNumberPosY))
                switchNumber += 1

            while len(randomTicks) < qtdSwitches:
                a = random.randint(0, 17)
                if a not in randomTicks:
                    randomTicks.append(a)
                    correctSwitchSum -= 2 ** a

            for rr in randomTicks:
                pygame.draw.rect(screen, GRAY, pygame.Rect(switchesPosX + 50 * rr, switchesPosY, 40, switchesPosX+20))
                numberLabel = gameFont.render(str(rr), 1, GRAY)
                screen.blit(numberLabel, (switchNumberPosX + 50 * rr, switchNumberPosY))
                pygame.display.update()
                time.sleep(speed)
                pygame.draw.rect(screen, WHITE, pygame.Rect(switchesPosX + 50 * rr, switchesPosY, 40, switchesPosX+20))
                numberLabel = gameFont.render(str(rr), 1, WHITE)
                screen.blit(numberLabel, (switchNumberPosX + 50 * rr, switchNumberPosY))
                pygame.display.update()
                time.sleep(speed)

            data = 15
            while data == 15:
                ioctl(fd, RD_SWITCHES)
                switchInput = os.read(fd, 4)
                switchInput = int.from_bytes(switchInput, 'little')
                
                ioctl(fd, RD_PBUTTONS)
                data = os.read(fd, 4)
                data = int.from_bytes(data, 'little')

            if(switchInput == correctSwitchSum):
                screen.fill(YELLOw)
                winFont = pygame.font.SysFont("comicsans", 150)
                levelWinLabel = winFont.render("Venceu!!!", 1, GREEN)
                screen.blit(levelWinLabel, (370, 300))
                levelWinClick = gameFont.render("Clique em algum botão para avançar para o próximo nível", 1, GREEN)
                screen.blit(levelWinClick, (130, 550))
                buttonClick = gameFont.render("Clique em algum botao para avançar", 1, GREEN)
                screen.blit(buttonClick, (270, 600))
                pygame.display.update()
                
                pontuacao += 10 * level 
                if pontuacao > 9999:
                    pontuacao = 9999

                speed -= 0.02
                # Se acertou, ligar os leds verdes e apagar os leds vermelhos.
                data = 0x0
                ioctl(fd, WR_RED_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))
                data = 0xFFFFFFFF
                ioctl(fd, WR_GREEN_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))
                time.sleep(3)
                # Depois disso, desligar os leds verdes.
                data = 0X0
                ioctl(fd, WR_GREEN_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))

                data = 15
                while data == 15:
                    ioctl(fd, RD_PBUTTONS)
                    data = os.read(fd, 4)
                    data = int.from_bytes(data, 'little')


            else:
                levelLoseLabel = gameFont.render("Perdeu", 1, RED)
                screen.blit(levelLoseLabel, (550, 300))
                pygame.display.update()
                #se errou ligar todos os leds vermelhos e apagar todos os leds verdes.
                data = 0xFFFFFFFF
                ioctl(fd, WR_RED_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))
                data = 0x0
                ioctl(fd, WR_GREEN_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))
                time.sleep(3)
                # Desligar os leds vermelhos
                data = 0x0
                ioctl(fd, WR_RED_LEDS)
                os.write(fd, data.to_bytes(4, 'little'))

                lose()

        level += 1
        if level % 2 == 0:
            buttonLevel += 1

        if level % 4 == 0:
            qtdSwitches += 1



        pygame.display.update()

    while running:

        clock.tick(FPS)
        redraw()
        randomTicks = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

def lose():
    global level
    global data
    global qtdSwitches
    global buttonLevel
    gameFont = pygame.font.SysFont("comicsans", 50)
    screen.fill(YELLOw)
    levelLoseLabel = gameFont.render("Perdeu", 1, RED)
    screen.blit(levelLoseLabel, (550, 300))
    restartLabel = gameFont.render("Aperte o primeiro botao para reiniciar", 1, RED)
    screen.blit(restartLabel, (300, 350))
    restartLabel = gameFont.render("Aperte qualquer outro botao para sair", 1, RED)
    screen.blit(restartLabel, (300, 400))

    pygame.display.update()

    data = 15
    while data == 15:
        ioctl(fd, RD_PBUTTONS)
        data = os.read(fd, 4)
        data = int.from_bytes(data, 'little')
        time.sleep(0.4)

    if data == 7:
        qtdSwitches = 3
        buttonLevel = 1
        main_menu()
    else:
        exit()
      
def main_menu():

    screen.blit(MENU_BACKGROUND, (0, 0))
    menuFont = pygame.font.SysFont("Helvetica", 50)
    menuLabel = menuFont.render("Jogo da memória", 1, WHITE)
    screen.blit(menuLabel, (140, 300))
    startLabel = menuFont.render("Clique para iniciar o jogo", 1, WHITE)
    screen.blit(startLabel, (20, 500))
    pygame.display.update()

    data = 0x0
    ioctl(fd, WR_RED_LEDS)
    os.write(fd, data.to_bytes(4, 'little'))
    ioctl(fd, WR_GREEN_LEDS)
    os.write(fd, data.to_bytes(4, 'little'))
    
    data = 0x40404040
    ioctl(fd, WR_R_DISPLAY)
    retval = os.write(fd, data.to_bytes(4, 'little'))

    runningMenu = True
    while runningMenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runningMenu = False
            elif event.type == pygame.MOUSEBUTTONUP:
                game()

main_menu()

os.close(fd)
