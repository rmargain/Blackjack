import random
import os
import sys
import pygame
from pygame.locals import *
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((900, 600))

def imageLoad(name, card):
    """Función para cargar una imagen. Se asegura de que el juego sea compatible en varios sistemas operativos, ya que
        usa la función os.path.join para obtener el nombre de archivo completo. Luego intenta cargar la imagen,
        y genera una excepción si no puede, por lo que el usuario sabrá específicamente qué sucede si la imagen se carga
        No funciona. """

    if card == 1:
        fullname = os.path.join("images/cards/", name)
    else: fullname = os.path.join('images', name)

    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert()

    return image, image.get_rect()

def soundLoad(name):
    """ Carga sonidos """

    fullName = os.path.join('sounds', name)
    try: sound = pygame.mixer.Sound(fullName)
    except pygame.error as message:
        print('Cannot load sound:', name)
        raise SystemExit(message)
    return sound

def display(font, sentence):
    """Muestra texto en la parte inferior de la pantalla, informando al jugador de lo que está sucediendo."""

    displayFont = pygame.font.Font.render(font, sentence, 1, (255,255,255), (0,0,0))
    return displayFont

def playClick():
    clickSound = soundLoad("click2.wav")
    clickSound.play()

#-------------------------------------------------------------------------------------

def mainGame():
    """Función que contiene toda la lógica del juego."""

    def gameOver():
        """Muestra una pantalla de finalización del juego. Se llama cuando se ha determinado que los fondos del jugador se han
        sin. Todo lo que el jugador puede hacer desde esta pantalla es salir del juego."""
        while 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit()

            # pone la pantalla en negro cuanado pierdes
            screen.fill((0,0,0))
            # imprime fin del juego
            oFont = pygame.font.Font(None, 50)
            displayFont = pygame.font.Font.render(oFont, "Fin del juego", 1, (255,255,255), (0,0,0))
            screen.blit(displayFont, (350, 300))
            # actualiza la pantalla
            pygame.display.flip()


    def shuffle(deck):
        """N es igual a la longitud del deck - 1 (porque el acceso a las listas comienza en 0 en lugar de 1). Si bien n es mayor que 0, un número aleatorio k entre 0
        y se genera n, y la carta en la baraja que está representada por el desplazamiento n se intercambia con la carta en la baraja
        representado por el desplazamiento k. Luego, n se reduce en 1 y el bucle continúa. """
        n = len(deck) - 1
        while n > 0:
            k = random.randint(0, n)
            deck[k], deck[n] = deck[n], deck[k]
            n -= 1
        return deck

    def createDeck():
        """Crea un mazo predeterminado que contiene las 52 cartas y lo devuelve."""
        deck = ['sj', 'sq', 'sk', 'sa', 'hj', 'hq', 'hk', 'ha', 'cj', 'cq', 'ck', 'ca', 'dj', 'dq', 'dk', 'da']
        values = range(2,11)
        for x in values:
            spades = "s" + str(x)
            hearts = "h" + str(x)
            clubs = "c" + str(x)
            diamonds = "d" + str(x)
            deck.append(spades)
            deck.append(hearts)
            deck.append(clubs)
            deck.append(diamonds)
        return deck

    def returnFromDead(deck, deadDeck):
        """Agrega las cartas del mazo muerto al mazo que está en juego. Esto se llama cuando el mazo principal
        se ha vaciado. """
        for card in deadDeck:
            deck.append(card)
        del deadDeck[:]
        deck = shuffle(deck)
        return deck, deadDeck

    def deckDeal(deck, deadDeck):
        """Baraja el mazo, saca las 4 primeras cartas del mazo, las agrega a las manos del jugador y del crupier, y
        devuelve las manos del jugador y del crupier. """
        deck = shuffle(deck)
        dealerHand, playerHand = [], []
        cardsToDeal = 4

        while cardsToDeal > 0:
            if len(deck) == 0:
                deck, deadDeck = returnFromDead(deck, deadDeck)
            """repartir la primera carta al jugador, la segunda al crupier, la tercera al jugador, la cuarta al crupier, 
            según la divisibilidad (comienza en 4, por lo que es incluso la primera)"""
            if cardsToDeal % 2 == 0: playerHand.append(deck[0])
            else: dealerHand.append(deck[0])
            del deck[0]
            cardsToDeal -= 1
        return deck, deadDeck, playerHand, dealerHand

    def hit(deck, deadDeck, hand):
        """Comprueba si la baraja se ha ido, en cuyo caso toma las cartas de
        la baraja muerta (cartas que se han jugado y descartado)
        y los mezcla. Luego, si el jugador está golpeando, le da
        una carta al jugador, o si el crupier está pidiendo, le da una al crupier. """
        # si la baraja está vacía, baraja en la baraja muerta
        if len(deck) == 0:
            deck, deadDeck = returnFromDead(deck, deadDeck)
        hand.append(deck[0])
        del deck[0]
        return deck, deadDeck, hand

    def checkFCard(hand):
        FcardValue = 0

        for card in hand:
            value = card[1:]
            if value == 'j' or value == 'q' or value == 'k':
                value = 10
            elif value == 'a':
                value = 11
            else: value = int(value)
            FcardValue= value
        return FcardValue

    def checkValue(hand):
        """Comprueba el valor de las cartas en la mano del jugador o del crupier."""
        totalValue = 0

        for card in hand:
            value = card[1:]
            # Jotas, reyes y reinas valen 10, y as vale 11
            if value == 'j' or value == 'q' or value == 'k': value = 10
            elif value == 'a': value = 11
            else: value = int(value)
            totalValue += value

        if totalValue > 21:
            for card in hand:
                # Si el jugador se pasa y tiene un as en la mano, el valor del as se reduce en 10
                """En situaciones en las que hay varios ases en la mano, esto comprueba si el valor total
                aún estaría por encima de 21 si el segundo as no se cambiara a un valor de uno. Si es menor de 21, no es necesario
                para cambiar el valor del segundo as, para que el bucle se rompa """
                if card[1] == 'a':
                    totalValue -= 10
                if totalValue <= 21:
                    break
                else:
                    continue
        return totalValue


    def blackJack(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite):
        """Se llama cuando se determina que el jugador o el crupier tiene blackjack.
        Las manos se comparan para determinar el resultado."""
        textFont = pygame.font.Font(None, 28)

        playerValue = checkValue(playerHand)
        dealerValue = checkValue(dealerHand)

        if playerValue == 21 and dealerValue == 21:
            # El jugador contrario empata al jugador original de blackjack porque también tiene blackjack
            # No se perderá dinero y se repartirá una nueva mano
            displayFont = display(textFont, "El dealer tiene BlackJack")
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, 0, bet, cards, cardSprite)
        elif playerValue == 21 and dealerValue != 21:
            # El dealer pierde
            displayFont = display(textFont, "Blackjack ganaste +$%.2f." %(bet*1.5))
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, bet, 0, cards, cardSprite)
        elif dealerValue == 21 and playerValue != 21:
            # El jugador pierde, se pierde dinero y se repartirá una nueva mano
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, 0, bet, cards, cardSprite)
            displayFont = display(textFont, "El dealer tiene blackjack! pierdes -$%.2f." %(bet))
        return displayFont, playerHand, dealerHand, deadDeck, funds, roundEnd

    def bust(deck, playerHand, dealerHand, deadDeck, funds, moneyGained, moneyLost, cards, cardSprite):
        """Esto solo se llama cuando el jugador tiene mas de 21"""
        font = pygame.font.Font(None, 28)
        displayFont = display(font, "Tienes mas de 21 -$%.2f." %(moneyLost))
        deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, moneyGained, moneyLost, cards, cardSprite)
        return deck, playerHand, dealerHand, deadDeck, funds, roundEnd, displayFont

    def endRound(deck, playerHand, dealerHand, deadDeck, funds, moneyGained, moneyLost, cards, cardSprite):
        """Se llama al final de una ronda para determinar qué sucede con las cartas, el dinero que ganó o perdió
        También muestra la mano del crupier al jugador, eliminando los sprites antiguos y mostrando todas las cartas. """

        if len(playerHand) == 2 and "a" in playerHand[0] or "a" in playerHand[1]:
            # Si el jugador tiene blackjack, devuelva su apuesta 3: 2
            moneyGained += (moneyGained/2.0)
        # Retira las cartas antiguas del crupier
        cards.empty()

        dCardPos = (420, 110)

        for x in dealerHand:
            card = cardSprite(x, dCardPos)
            dCardPos = (dCardPos[0] + 20, dCardPos [1])

            cards.add(card)


            # Retire las cartas de las manos del jugador y del crupier
        for card in playerHand:
            deadDeck.append(card)
        for card in dealerHand:
            deadDeck.append(card)

        del playerHand[:]
        del dealerHand[:]

        funds += moneyGained
        funds -= moneyLost

        textFont = pygame.font.Font(None, 28)

        if funds <= 0:
            gameOver()

        roundEnd = 1

        return deck, playerHand, dealerHand, deadDeck, funds, roundEnd

    def compareHands(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite):
        """Se llama al final de una ronda (después de que el jugador se pone de pie) o al comienzo de una ronda
        si el jugador o el crupier tiene blackjack. Esta función compara los valores de las respectivas manos de
        el jugador y el crupier y determina quién gana la ronda según las reglas del blacjack. """

        textFont = pygame.font.Font(None, 28)
        #Cuánto dinero pierde o gana el jugador, predeterminado en 0, cambia según el resultado

        moneyGained= 0
        moneylost= 0

        dealerValue = checkValue(dealerHand)
        playerValue = checkValue(playerHand)

        # El crupier golpea hasta que tenga 17 o más
        while 1:
            if dealerValue < 17:
                # dealer hits when he has less than 17, and stands if he has 17 or above
                deck, deadDeck, dealerHand = hit(deck, deadDeck, dealerHand)
                dealerValue = checkValue(dealerHand)
            else:
                # el dealer para
                break

        if playerValue > dealerValue and playerValue <= 21:
            # El jugador ha vencido al crupier y no ha sido eliminado, por lo tanto gana
            moneyGained = bet
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, bet, 0, cards, cardSprite)
            displayFont = display(textFont, "Ganaste +$%.2f." %(bet))
        elif playerValue == dealerValue and playerValue <= 21:
            # empate
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, 0, 0, cards, cardSprite)
            displayFont = display(textFont, "EMPATE!")
        elif dealerValue > 21 and playerValue <= 21:
            # El crupier se paso  y el jugador no
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, bet, 0, cards, cardSprite)
            displayFont = display(textFont, "El dealer se paso. Ganaste +$%.2f." %(bet))
        else:
            # El distribuidor gana en todas las demás situaciones que se me ocurren
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, 0, bet, cards, cardSprite)
            displayFont = display(textFont, "El dealer ganó, tu pierdes +$%.2f." %(bet))

        return deck, deadDeck, roundEnd, funds, displayFont

    """aqui empieza pygame en su mayoria de codigo"""

    class cardSprite(pygame.sprite.Sprite):
        """Sprite que muestra una tarjeta específica."""

        def __init__(self, card, position):
            pygame.sprite.Sprite.__init__(self)
            cardImage = card + ".png"
            self.image, self.rect = imageLoad(cardImage, 1)
            self.position = position
        def update(self):
            self.rect.center = self.position

    class hitButton(pygame.sprite.Sprite):
        """Botón que permite al jugador pedir (HIT)."""

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("hit-grey.png", 0)
            self.position = (735, 400)

        def update(self, mX, mY, deck, deadDeck, playerHand, cards, pCardPos, roundEnd, cardSprite, click):
            """Si se hace clic en el botón y la ronda NO ha terminado, golpea al jugador con una nueva carta de la baraja. A continuación, crea un objeto
            para la tarjeta y la muestra. """
            if roundEnd == 0: self.image, self.rect = imageLoad("hit.png", 0)
            else: self.image, self.rect = imageLoad("hit-grey.png", 0)
            self.position = (850, 522)
            self.rect.center = self.position

            if self.rect.collidepoint(mX, mY) == 1 and click == 1:
                if roundEnd == 0:
                    playClick()
                    deck, deadDeck, playerHand = hit(deck, deadDeck, playerHand)
                    currentCard = len(playerHand) - 1
                    card = cardSprite(playerHand[currentCard], pCardPos)
                    cards.add(card)
                    pCardPos = (pCardPos[0] + 20, pCardPos[1])
                    click = 0
            return deck, deadDeck, playerHand, pCardPos, click

    class standButton(pygame.sprite.Sprite):
        """Botón que no  permite al jugador tomar más cartas"""

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("stand-grey.png", 0)
            self.position = (735, 365)
        def update(self, mX, mY, deck, deadDeck, playerHand, dealerHand, cards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont):
            """Si se hace clic en el botón y la ronda NO ha terminado,
            deje que el jugador se pare (no tome más cartas)."""
            if roundEnd == 0: self.image, self.rect = imageLoad("stand.png", 0)
            else: self.image, self.rect = imageLoad("stand-grey.png", 0)
            self.position = (850, 483)
            self.rect.center = self.position
            if self.rect.collidepoint(mX, mY) == 1:
                if roundEnd == 0:
                    playClick()
                    deck, deadDeck, roundEnd, funds, displayFont = compareHands(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite)
            return deck, deadDeck, roundEnd, funds, playerHand, deadDeck, pCardPos, displayFont

    class doubleButton(pygame.sprite.Sprite):
        """Botón que permite al jugador doblar (doblar la apuesta, tomar una carta más y luego plantarse)."""

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("double-grey.png", 0)
            self.position = (735, 330)

        def update(self, mX, mY,   deck, deadDeck, playerHand, dealerHand, playerCards, cards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont):
            """Si se hace clic en el botón y la ronda NO ha terminado, deje que el jugador se pare (no tome más cartas)."""
            if roundEnd == 0 and funds >= bet * 2 and len(playerHand) == 2: self.image, self.rect = imageLoad("double.png", 0)
            else: self.image, self.rect = imageLoad("double-grey.png", 0)
            self.position = (850, 442)
            self.rect.center = self.position

            if self.rect.collidepoint(mX, mY) == 1:
                if roundEnd == 0 and funds >= bet * 2 and len(playerHand) == 2:
                    bet = bet * 2
                    playClick()
                    deck, deadDeck, playerHand = hit(deck, deadDeck, playerHand)
                    currentCard = len(playerHand) - 1
                    card = cardSprite(playerHand[currentCard], pCardPos)
                    playerCards.add(card)
                    pCardPos = (pCardPos[0] - 80, pCardPos[1])
                    deck, deadDeck, roundEnd, funds, displayFont = compareHands(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite)
                    bet = bet / 2
            return deck, deadDeck, roundEnd, funds, playerHand, deadDeck, pCardPos, displayFont, bet

    class dealButton(pygame.sprite.Sprite):
        """Un botón en el lado derecho de la pantalla que se puede hacer clic al final de una ronda para repartir un
        nueva mano de cartas y continuar el juego. """
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("deal.png", 0)
            self.position = (735, 450)

        def update(self, mX, mY, deck, deadDeck, roundEnd, cardSprite, cards, playerHand, dealerHand, dCardPos, pCardPos, displayFont, playerCards, click, handsPlayed):
            """El botón de reparto solo se puede presionar
            después de que la ronda haya terminado
            y se ha declarado un ganador. """

            textFont = pygame.font.Font(None, 28)

            if roundEnd == 1: self.image, self.rect = imageLoad("deal.png", 0)
            else: self.image, self.rect = imageLoad("deal-grey.png", 0)

            self.position = (850, 560)
            self.rect.center = self.position


            if self.rect.collidepoint(mX, mY) == 1:
                if roundEnd == 1 and click == 1:
                    playClick()
                    displayFont = display(textFont, "")

                    cards.empty()
                    playerCards.empty()

                    deck, deadDeck, playerHand, dealerHand = deckDeal(deck, deadDeck)

                    dCardPos = (420, 110)
                    pCardPos = (440,370)

                    # Cartas de jugador
                    for x in playerHand:
                        card = cardSprite(x, pCardPos)
                        pCardPos = (pCardPos[0] + 20, pCardPos[1])
                        playerCards.add(card)

                    # Cartas del dealer
                    faceDownCard = cardSprite("back", dCardPos)
                    dCardPos = (dCardPos[0] + 20, dCardPos[1])
                    cards.add(faceDownCard)

                    card = cardSprite(dealerHand[0], dCardPos)
                    cards.add(card)
                    roundEnd = 0
                    click = 0
                    handsPlayed += 1

            return deck, deadDeck, playerHand, dealerHand, dCardPos, pCardPos, roundEnd, displayFont, click, handsPlayed


    class betButtonUp(pygame.sprite.Sprite):
        """Botón que permite al jugador aumentar su apuesta ."""
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("up.png", 0)
            self.position = (710, 255)
        def update(self, mX, mY, bet, funds, click, roundEnd):
            if roundEnd == 1: self.image, self.rect = imageLoad("up.png", 0)
            else: self.image, self.rect = imageLoad("up-grey.png", 0)
            self.position = (40, 500)
            self.rect.center = self.position
            if self.rect.collidepoint(mX, mY) == 1 and click == 1 and roundEnd == 1:
                playClick()

                if bet < funds:
                    bet += 5.0
                    # Si la apuesta no es múltiplo de 5, conviértala en múltiplo de 5
                    # Esto solo puede suceder cuando el jugador ha obtenido blackjack y tiene fondos que no son divisibles por 5,
                    # luego pierde dinero y tiene una apuesta más alta que sus fondos, por lo que la apuesta se reduce a los fondos, que son desiguales.
                    if bet % 5 != 0:
                        while bet % 5 != 0:
                            bet -= 1
                click = 0
            return bet, click

    class betButtonDown(pygame.sprite.Sprite):
        """Botón que permite al jugador disminuir su apuesta ."""

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("down.png", 0)
            self.position = (710, 255)
        def update(self, mX, mY, bet, click, roundEnd):
            if roundEnd == 1: self.image, self.rect = imageLoad("down.png", 0)
            else: self.image, self.rect = imageLoad("down-grey.png", 0)
            self.position = (40, 560)
            self.rect.center = self.position
            if self.rect.collidepoint(mX, mY) == 1 and click == 1 and roundEnd == 1:
                playClick()
                if bet > 5:
                    bet -= 5.0
                    if bet % 5 != 0:
                        while bet % 5 != 0:
                            bet += 1
                click = 0
            return bet, click


    # se utiliza para mostrar texto en la pantalla.
    textFont = pygame.font.Font(None, 28)
    textFont2 = pygame.font.Font(None, 15)

    # Esto configura la imagen de fondo y su contenedor rect
    background, backgroundRect = imageLoad("bjs.png", 0)

    # cards es el grupo de sprites que contendrá sprites para las cartas del crupier
    cards = pygame.sprite.Group()
    # playerCards tendrá el mismo propósito, pero para el jugador
    playerCards = pygame.sprite.Group()

    #aqui se lleva registro del numero de cartas

    playerValue= 0
    dealerValue= 0

    # Esto crea instancias de todos los sprites de botón.
    bbU = betButtonUp()
    bbD = betButtonDown()
    standButton = standButton()
    dealButton = dealButton()
    hitButton = hitButton()
    doubleButton = doubleButton()

    # Este grupo contiene el botón sprite
    buttons = pygame.sprite.Group(bbU, bbD, hitButton, standButton, dealButton, doubleButton)

    #el maso se crea
    deck = createDeck()
    # La baraja muerta contendrá cartas descartadas.
    deadDeck = []

    # Estos son valores predeterminados que se cambiarán más adelante, pero deben declararse ahora
    # para que Python no se confunda
    playerHand, dealerHand, dCardPos, pCardPos = [],[],(),()
    mX, mY = 0, 0
    click = 0

    # Los fondos predeterminados comienzan en $ 100,00 y la apuesta inicial es de $ 10,00
    funds = 100.00
    bet = 10.00

    # Los fondos predeterminados comienzan en $ 100,00 y la apuesta inicial es de $ 10,00
    handsPlayed = 0

    # Cuando se han repartido las cartas, roundEnd es cero.
    # Entre rondas, es igual a uno
    roundEnd = 1

    # firstTime es una variable que solo se usa una vez, para mostrar la inicial
    # en la parte inferior, luego se establece en cero durante la duración del programa.
    firstTime = 1


    while 1:
        screen.blit(background, backgroundRect)

        if bet > funds:
            # Si perdió dinero y su apuesta es mayor que sus fondos, haga que la apuesta sea igual a los fondos
            bet = funds

        if roundEnd == 1 and firstTime == 1:
            # Cuando el jugador no ha comenzado. Solo se mostrará la primera vez.
            displayFont = display(textFont, "")
            firstTime = 0

        #muestra nuestros nombres
        countFont = pygame.font.Font.render(textFont2,"Alfonso Reyes", 1, (0, 0, 0))
        screen.blit(countFont, (20, 20))
        countFont = pygame.font.Font.render(textFont2, "Roberto Margin", 1, (0, 0, 0))
        screen.blit(countFont, (20, 30))

        # muestra el proceso del juego
        screen.blit(displayFont, (10,444))
        fundsFont = pygame.font.Font.render(textFont, "fichas: $%.2f" %(funds), 1, (255,255,255), (0,0,0))
        screen.blit(fundsFont, (700,0))
        betFont = pygame.font.Font.render(textFont, "tu apuesta: $%.2f" %(bet), 1, (255,255,255), (0,0,0))
        screen.blit(betFont, (370,0))
        hpFont = pygame.font.Font.render(textFont, "Rounda: %i " %(handsPlayed), 1, (255,255,255), (0,0,0))
        screen.blit(hpFont, (0,0))
        countFont = pygame.font.Font.render(textFont, str(playerValue), 1, (0, 0, 0))
        screen.blit(countFont, (445,530))


        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mX, mY = pygame.mouse.get_pos()
                    click = 1
            elif event.type == MOUSEBUTTONUP:
                mX, mY = 0, 0
                click = 0

        # Verificación inicial del valor de la mano del jugador, de modo que su mano pueda mostrarse y pueda determinarse
        # si el jugador pasa o tiene blackjack o no
        if roundEnd == 0:
            # Cosas para hacer cuando el juego está sucediendo
            playerValue = checkValue(playerHand)
            dealerValue = checkValue(dealerHand)
            FcardValue = checkFCard(dealerHand)

            if playerValue == 21 and len(playerHand) == 2:
                # Si el jugador obtiene blackjack
                displayFont, playerHand, dealerHand, deadDeck, funds, roundEnd = blackJack(deck, deadDeck, playerHand, dealerHand, funds,  bet, cards, cardSprite)

            if dealerValue == 21 and len(dealerHand) == 2:
                # Si el crupier tiene blackjack
                displayFont, playerHand, dealerHand, deadDeck, funds, roundEnd = blackJack(deck, deadDeck, playerHand, dealerHand, funds,  bet, cards, cardSprite)

            if playerValue > 21:
                # Si el jugador se arruina
                deck, playerHand, dealerHand, deadDeck, funds, roundEnd, displayFont = bust(deck, playerHand, dealerHand, deadDeck, funds, 0, bet, cards, cardSprite)

        # Actualizar los botones
        # trato
        deck, deadDeck, playerHand, dealerHand, dCardPos, pCardPos, roundEnd, displayFont, click, handsPlayed = dealButton.update(mX, mY, deck, deadDeck, roundEnd, cardSprite, cards, playerHand, dealerHand, dCardPos, pCardPos, displayFont, playerCards, click, handsPlayed)
        # hit    
        deck, deadDeck, playerHand, pCardPos, click = hitButton.update(mX, mY, deck, deadDeck, playerHand, playerCards, pCardPos, roundEnd, cardSprite, click)
        # stand    
        deck, deadDeck, roundEnd, funds, playerHand, deadDeck, pCardPos,  displayFont  = standButton.update(mX, mY,   deck, deadDeck, playerHand, dealerHand, cards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont)
        # double
        deck, deadDeck, roundEnd, funds, playerHand, deadDeck, pCardPos, displayFont, bet  = doubleButton.update(mX, mY,   deck, deadDeck, playerHand, dealerHand, playerCards, cards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont)
        # botones de apuesta
        bet, click = bbU.update(mX, mY, bet, funds, click, roundEnd)
        bet, click = bbD.update(mX, mY, bet, click, roundEnd)
        # dibujarlos en la pantalla
        buttons.draw(screen)

        # Si hay cartas en la pantalla, robalas
        if len(cards) != 0:
            playerCards.update()
            playerCards.draw(screen)
            cards.update()
            cards.draw(screen)

        # actuliza el conenido en la pantalla
        pygame.display.flip()

if __name__ == "__main__":
    mainGame()
