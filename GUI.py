import sys
from main import solve
import pygame

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
BLOCK_SIDE = 60
SUDOKU_WIDTH = BLOCK_SIDE*9
SUDOKU_HEIGHT = BLOCK_SIDE*9
SCREEN_WIDTH = SUDOKU_WIDTH
SCREEN_HEIGHT = BLOCK_SIDE*9 + 100

sudoku_example = [
    [-1, -1, -1, 9, -1, -1, -1, 8, -1],
    [6, 4, -1, 8, -1, 1, 3, 9, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, 3, -1, 2, -1, 9, -1, 1, -1],
    [-1, -1, -1, -1, 6, -1, -1, -1, -1],
    [-1, 6, -1, 1, -1, 4, -1, 5, -1],
    [-1, -1, -1, -1, -1, -1, -1, 4, -1],
    [-1, 9, 4, 7, -1, 6, -1, 2, 1],
    [-1, 7, -1, -1, -1, 2, -1, -1, -1]
]

def drawGrid(sudoku, selected=None):
    font = pygame.font.Font('freesansbold.ttf', 32)
    for x in range(9):
        for y in range(9):
            color = BLACK
            selection_size = 1
            w = h = BLOCK_SIDE
            if selected is not None and y == selected[0]-1 and x == selected[1]-1:
                color = RED
                selection_size = 2
                w = h = BLOCK_SIDE-1
            rect = pygame.Rect(x*BLOCK_SIDE, y*BLOCK_SIDE, w, h)
            pygame.draw.rect(SCREEN, color, rect, selection_size)
            if 1 <= sudoku[y][x] <= 9:
                text = font.render(str(sudoku[y][x]), True, BLACK, WHITE)
                text_rect = text.get_rect()
                text_rect.center = (x*BLOCK_SIDE + BLOCK_SIDE/2, y*BLOCK_SIDE+BLOCK_SIDE/2)
                SCREEN.blit(text, text_rect)

    pygame.draw.line(SCREEN, BLUE, (3 * BLOCK_SIDE - 1, 0), (3 * BLOCK_SIDE - 1, 9 * BLOCK_SIDE), width=3)
    pygame.draw.line(SCREEN, BLUE, (6 * BLOCK_SIDE - 1, 0), (6 * BLOCK_SIDE - 1, 9 * BLOCK_SIDE), width=3)
    pygame.draw.line(SCREEN, BLUE, (0, 3 * BLOCK_SIDE - 1), (9 * BLOCK_SIDE, 3 * BLOCK_SIDE - 1), width=3)
    pygame.draw.line(SCREEN, BLUE, (0, 6 * BLOCK_SIDE - 1), (9 * BLOCK_SIDE, 6 * BLOCK_SIDE - 1), width=3)

    reset_text = font.render("Reset", True, BLACK, WHITE)
    reset_text_rect = reset_text.get_rect()
    reset_text_rect.center = (SUDOKU_WIDTH/4, SUDOKU_HEIGHT + (SCREEN_HEIGHT - SUDOKU_HEIGHT)/2)
    SCREEN.blit(reset_text, reset_text_rect)
    solve_text = font.render("Solve", True, BLACK, WHITE)
    solve_text_rect = reset_text.get_rect()
    solve_text_rect.center = (SUDOKU_WIDTH*3/4, SUDOKU_HEIGHT + (SCREEN_HEIGHT - SUDOKU_HEIGHT)/2)
    SCREEN.blit(solve_text, solve_text_rect)


def setCell(sudoku, cell, value):
    sudoku[cell[0]-1][cell[1]-1] = value


def reset(sudoku):
    for i in range(1, 10):
        for j in range(1, 10):
            setCell(sudoku, (i, j), -1)


if __name__ == '__main__':
    pygame.init()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    CLOCK = pygame.time.Clock()
    selected_cell = None
    sudoku = [[val for val in row] for row in sudoku_example]
    run = True
    while run:
        SCREEN.fill(WHITE)
        drawGrid(sudoku, selected=selected_cell)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if pos[1] <= SUDOKU_HEIGHT and pos[0] <= SUDOKU_WIDTH:
                    row = pos[1]//BLOCK_SIDE + 1
                    column = pos[0] // BLOCK_SIDE + 1
                    selected_cell = (row, column)
                elif SUDOKU_HEIGHT <= pos[1] <= SCREEN_HEIGHT and pos[0] <= SUDOKU_WIDTH/2:
                    # Reset
                    sudoku = [[val for val in row] for row in sudoku_example]
                elif SUDOKU_HEIGHT <= pos[1] <= SCREEN_HEIGHT and pos[0] >= SUDOKU_WIDTH/2:
                    # Solve
                    sudoku = solve(sudoku)
                    if sudoku is None:
                        sudoku = [[val for val in row] for row in sudoku_example]
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    setCell(sudoku, selected_cell, 1)
                elif event.key == pygame.K_2:
                    setCell(sudoku, selected_cell, 2)
                elif event.key == pygame.K_3:
                    setCell(sudoku, selected_cell, 3)
                elif event.key == pygame.K_4:
                    setCell(sudoku, selected_cell, 4)
                elif event.key == pygame.K_5:
                    setCell(sudoku, selected_cell, 5)
                elif event.key == pygame.K_6:
                    setCell(sudoku, selected_cell, 6)
                elif event.key == pygame.K_7:
                    setCell(sudoku, selected_cell, 7)
                elif event.key == pygame.K_8:
                    setCell(sudoku, selected_cell, 8)
                elif event.key == pygame.K_9:
                    setCell(sudoku, selected_cell, 9)
                elif event.key == 8:  # DELETE
                    setCell(sudoku, selected_cell, -1)
                if selected_cell is not None:
                    if event.key == pygame.K_LEFT:
                        selected_cell = (selected_cell[0], selected_cell[1]-1 if selected_cell[1] > 1 else 9)
                    elif event.key == pygame.K_RIGHT:
                        selected_cell = (selected_cell[0], (selected_cell[1] % 9) + 1)
                    elif event.key == pygame.K_UP:
                        selected_cell = (selected_cell[0]-1 if selected_cell[0] > 1 else 9, selected_cell[1])
                    elif event.key == pygame.K_DOWN:
                        selected_cell = ((selected_cell[0] % 9) + 1, selected_cell[1])
        pygame.display.update()
