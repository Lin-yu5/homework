import os
import msvcrt
import random
import time
from collections import deque

def generate_maze(width=15, height=15):
    width = width if width % 2 == 1 else width + 1
    height = height if height % 2 == 1 else height + 1
    maze = [['#' for _ in range(width)] for _ in range(height)]
    stack = []
    sx, sy = 1, 1
    maze[sx][sy] = ' '
    stack.append((sx, sy))
    dirs = [(-2,0),(2,0),(0,-2),(0,2)]
    while stack:
        x, y = stack[-1]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < height-1 and 1 <= ny < width-1 and maze[nx][ny] == '#':
                maze[nx][ny] = ' '
                maze[x + dx//2][y + dy//2] = ' '
                stack.append((nx, ny))
                break
        else:
            stack.pop()
    maze[1][1] = 'P'
    maze[height-2][width-2] = 'E'
    return maze

def print_maze_fog(maze, steps, treasures, total_treasure, elapsed, score):
    x, y = find_player(maze)
    os.system('cls' if os.name == 'nt' else 'clear')
    for i, row in enumerate(maze):
        line = ''
        for j, cell in enumerate(row):
            if abs(i - x) <= 2 and abs(j - y) <= 2:
                line += cell
            else:
                line += ' '
        print(line)
    print(f"\n步數：{steps}  寶物：{treasures}/{total_treasure}  用時：{elapsed:.2f} 秒  分數：{score}")
    print("WASD移動，Q自動尋路，R重玩，Esc離開")

def find_player(maze):
    for i, row in enumerate(maze):
        for j, cell in enumerate(row):
            if cell == 'P':
                return i, j

def find_end(maze):
    for i, row in enumerate(maze):
        for j, cell in enumerate(row):
            if cell == 'E':
                return i, j

def bfs_path(maze):
    start = find_player(maze)
    end = find_end(maze)
    queue = deque()
    queue.append((start, []))
    visited = set()
    visited.add(start)
    dirs = [(-1,0),(1,0),(0,-1),(0,1)]
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            return path
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(maze) and 0 <= ny < len(maze[0]):
                if maze[nx][ny] in (' ', 'E') and (nx, ny) not in visited:
                    queue.append(((nx, ny), path + [(dx, dy)]))
                    visited.add((nx, ny))
    return []

def get_path(maze):
    path = bfs_path(maze)
    start = find_player(maze)
    px, py = start
    result = [(px, py)]
    for dx, dy in path:
        px += dx
        py += dy
        result.append((px, py))
    return result

def get_all_empty_cells(maze, exclude=set()):
    cells = []
    for i in range(1, len(maze)-1):
        for j in range(1, len(maze[0])-1):
            if maze[i][j] == ' ' and (i, j) not in exclude:
                cells.append((i, j))
    return cells

def place_treasure(maze, count=3, exclude=set()):
    cells = get_all_empty_cells(maze, exclude)
    random.shuffle(cells)
    for _ in range(min(count, len(cells))):
        x, y = cells.pop()
        maze[x][y] = '$'

def place_trap_safe(maze, count=2, path=set()):
    # 只排除通路
    cells = get_all_empty_cells(maze, path)
    random.shuffle(cells)
    for _ in range(min(count, len(cells))):
        x, y = cells.pop()
        maze[x][y] = 'X'

def move_player(maze, dx, dy, start_pos, treasures):
    x, y = find_player(maze)
    nx, ny = x + dx, y + dy
    if maze[nx][ny] in (' ', '$', 'E', 'X'):
        if maze[nx][ny] == 'E':
            maze[x][y] = ' '
            maze[nx][ny] = 'P'
            return 'win', treasures
        elif maze[nx][ny] == '$':
            treasures += 1
            maze[x][y] = ' '
            maze[nx][ny] = 'P'
            return 'move', treasures
        elif maze[nx][ny] == 'X':
            print("你踩到陷阱，被傳送回起點！")
            time.sleep(1)
            maze[x][y] = ' '
            sx, sy = start_pos
            maze[sx][sy] = 'P'
            return 'trap', treasures
        else:
            maze[x][y] = ' '
            maze[nx][ny] = 'P'
            return 'move', treasures
    return 'none', treasures

def main():
    while True:
        # 產生有解的迷宮
        while True:
            maze = generate_maze(15, 15)
            path = set(get_path(maze))
            if len(path) > 1:
                break
        start_pos = find_player(maze)
        total_treasure = random.randint(2, 5)

        place_treasure(maze, total_treasure)  # 不排除通路
        place_trap_safe(maze, random.randint(1, 3), path)  # 只排除通路
        treasures = 0
        steps = 0
        start_time = time.time()
        score = 0
        print_maze_fog(maze, steps, treasures, total_treasure, 0, score)
        while True:
            elapsed = time.time() - start_time
            score = treasures * 100 - steps
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in [b'\x1b']:  # Esc
                    print("遊戲結束！")
                    return
                key = key.decode('utf-8').lower()
                win = False
                if key == 'w':
                    result, treasures = move_player(maze, -1, 0, start_pos, treasures)
                    if result in ('move', 'win'):
                        steps += 1
                    if result == 'win':
                        win = True
                elif key == 's':
                    result, treasures = move_player(maze, 1, 0, start_pos, treasures)
                    if result in ('move', 'win'):
                        steps += 1
                    if result == 'win':
                        win = True
                elif key == 'a':
                    result, treasures = move_player(maze, 0, -1, start_pos, treasures)
                    if result in ('move', 'win'):
                        steps += 1
                    if result == 'win':
                        win = True
                elif key == 'd':
                    result, treasures = move_player(maze, 0, 1, start_pos, treasures)
                    if result in ('move', 'win'):
                        steps += 1
                    if result == 'win':
                        win = True
                elif key == 'r':
                    print("重新開始！")
                    time.sleep(1)
                    break
                elif key == 'q':
                    path_seq = bfs_path(maze)
                    for dx, dy in path_seq:
                        result, treasures = move_player(maze, dx, dy, start_pos, treasures)
                        if result in ('move', 'win'):
                            steps += 1
                        print_maze_fog(maze, steps, treasures, total_treasure, time.time()-start_time, treasures*100-steps)
                        if result == 'win':
                            win = True
                            break
                        time.sleep(0.05)
                    if win:
                        elapsed = time.time() - start_time
                        score = treasures * 100 - steps
                        print(f"\n自動尋路完成，恭喜你走出迷宮！")
                        print(f"總步數：{steps}，寶物：{treasures}/{total_treasure}，用時：{elapsed:.2f} 秒，分數：{score}")
                        input("按任意鍵繼續...")
                        break
                    continue
                print_maze_fog(maze, steps, treasures, total_treasure, time.time()-start_time, treasures*100-steps)
                if win:
                    elapsed = time.time() - start_time
                    score = treasures * 100 - steps
                    print(f"\n恭喜你走出迷宮！")
                    print(f"總步數：{steps}，寶物：{treasures}/{total_treasure}，用時：{elapsed:.2f} 秒，分數：{score}")
                    input("按任意鍵繼續...")
                    break

if __name__ == "__main__":
    main()