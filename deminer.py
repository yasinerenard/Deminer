import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900

# Grid size (modifiable)
GRID_SIZE = 30  # Change this to your desired size (e.g., 10, 20, 100)

# Calculate bombs and cell size dynamically
BOMBS = GRID_SIZE * GRID_SIZE // 10  # 1 bomb per 10 cells
CELL_SIZE = min((SCREEN_WIDTH - 100) // GRID_SIZE, (SCREEN_HEIGHT - 200) // GRID_SIZE)
MARGIN = 2  # Space between cells

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Calculate grid position to center it
GRID_WIDTH = GRID_SIZE * (CELL_SIZE + MARGIN) - MARGIN
GRID_HEIGHT = GRID_SIZE * (CELL_SIZE + MARGIN) - MARGIN
GRID_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2 - 50  # Adjust for buttons

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Démineur")
font = pygame.font.Font(None, 24)

# Create grid
def create_grid():
    grid = []
    for _ in range(GRID_SIZE):
        grid.append([0] * GRID_SIZE)
    return grid

# Place bombs
def place_bombs(grid):
    for _ in range(BOMBS):
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            if grid[y][x] == 0:
                grid[y][x] = -1
                break

# Calculate numbers
def calculate_numbers(grid):
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] == -1:
                continue
            count = 0
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny][nx] == -1:
                    count += 1
            grid[y][x] = count

# Reveal empty cells using a flood-fill algorithm
def reveal_empty_cells(grid, revealed, x, y):
    stack = [(x, y)]
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    while stack:
        cx, cy = stack.pop()
        if not (0 <= cx < GRID_SIZE and 0 <= cy < GRID_SIZE):
            continue
        if revealed[cy][cx]:
            continue

        revealed[cy][cx] = True

        if grid[cy][cx] == 0:  # Continue spreading only if the cell is empty
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and not revealed[ny][nx]:
                    stack.append((nx, ny))

# Draw the grid
def draw_grid(grid, revealed, flagged):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(GRID_X + x * (CELL_SIZE + MARGIN), 
                               GRID_Y + y * (CELL_SIZE + MARGIN), 
                               CELL_SIZE, CELL_SIZE)
            if revealed[y][x]:
                color = WHITE if grid[y][x] != -1 else RED
                pygame.draw.rect(screen, color, rect)
                if grid[y][x] > 0:
                    text = font.render(str(grid[y][x]), True, BLACK)
                    screen.blit(text, text.get_rect(center=rect.center))
            elif flagged[y][x]:
                pygame.draw.rect(screen, YELLOW, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

# Draw flag counter
def draw_flag_counter(flags_placed):
    remaining_flags = BOMBS - sum([sum(row) for row in flags_placed])
    counter_text = font.render(f'Flags Remaining: {remaining_flags}', True, RED)
    screen.blit(counter_text, (SCREEN_WIDTH - 250, 10))

# Reveal an untrapped (non-bomb) cell at the start of the game
def reveal_random_safe_cell(grid, revealed):
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if grid[y][x] != -1 and not revealed[y][x]:  # Ensure it's not a bomb
            reveal_empty_cells(grid, revealed, x, y)
            break

# Main game loop
def main():
    def reset_game():
        nonlocal grid, revealed, flagged
        grid = create_grid()
        place_bombs(grid)
        calculate_numbers(grid)
        revealed = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        flagged = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        reveal_random_safe_cell(grid, revealed)  # Reveal an untrapped cell

    grid = create_grid()
    place_bombs(grid)
    calculate_numbers(grid)
    revealed = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
    flagged = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]

    running = True

    # Buttons
    solve_button = pygame.Rect(SCREEN_WIDTH // 2 - 260, GRID_Y + GRID_HEIGHT + 20, 150, 40)
    restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, GRID_Y + GRID_HEIGHT + 20, 150, 40)

    while running:
        screen.fill(BLACK)

        # Draw the grid and buttons
        draw_grid(grid, revealed, flagged)
        draw_flag_counter(flagged)
        pygame.draw.rect(screen, GREEN, solve_button)
        solve_text = font.render("Solve", True, BLACK)
        screen.blit(solve_text, solve_text.get_rect(center=solve_button.center))

        pygame.draw.rect(screen, BLUE, restart_button)
        restart_text = font.render("Restart", True, WHITE)
        screen.blit(restart_text, restart_text.get_rect(center=restart_button.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if solve_button.collidepoint(x, y):
                    revealed = [[True] * GRID_SIZE for _ in range(GRID_SIZE)]
                elif restart_button.collidepoint(x, y):
                    reset_game()
                else:
                    for row in range(GRID_SIZE):
                        for col in range(GRID_SIZE):
                            rect = pygame.Rect(GRID_X + col * (CELL_SIZE + MARGIN), 
                                               GRID_Y + row * (CELL_SIZE + MARGIN), 
                                               CELL_SIZE, CELL_SIZE)
                            if rect.collidepoint(x, y):
                                if event.button == 3:  # Right-click to flag
                                    flagged[row][col] = not flagged[row][col]
                                elif not flagged[row][col]:  # Ignore clicks on flagged cells
                                    if grid[row][col] == -1:
                                        revealed = [[True] * GRID_SIZE for _ in range(GRID_SIZE)]
                                    elif grid[row][col] == 0:
                                        reveal_empty_cells(grid, revealed, col, row)
                                    else:
                                        revealed[row][col] = True

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
