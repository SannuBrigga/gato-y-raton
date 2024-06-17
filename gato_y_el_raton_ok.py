import tkinter as tk
import random
import tkinter.messagebox

class JuegoGatoRaton:
    def __init__(self, raiz):
        self.tamaño = 6
        self.raiz = raiz
        self.tablero = [[0] * self.tamaño for _ in range(self.tamaño)]
        self.gato_pos = (0, 0)
        self.raton_pos = self.generar_posicion_aleatoria(exclude=[self.gato_pos])
        self.ruta_escape = self.generar_posicion_aleatoria(exclude=[self.gato_pos, self.raton_pos])
        self.turno_raton = True
        self.canvas = tk.Canvas(raiz, width=400, height=400)
        self.canvas.pack()
        self.dibujar_tablero()
        self.raiz.bind("<KeyPress>", self.seleccionar_celda)

    def generar_posicion_aleatoria(self, exclude=[]):
        while True:
            x = random.randint(0, self.tamaño - 1)
            y = random.randint(0, self.tamaño - 1)
            pos = (x, y)
            if pos not in exclude:
                return pos

    def dibujar_tablero(self):
        self.canvas.delete("all")
        tamaño_celda = 400 // self.tamaño
        colores = ["yellow", "white"]
        for fila in range(self.tamaño):
            for columna in range(self.tamaño):
                x1, y1 = fila * tamaño_celda, columna * tamaño_celda
                x2, y2 = x1 + tamaño_celda, y1 + tamaño_celda
                color = colores[(fila + columna) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                if (fila, columna) == self.ruta_escape:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="green")
        self.actualizar_posiciones()

    def actualizar_posiciones(self):
        tamaño_celda = 400 // self.tamaño
        gato_x, gato_y = self.gato_pos
        raton_x, raton_y = self.raton_pos
        # Dibujar gato (círculo naranja grande)
        self.canvas.create_oval(gato_x * tamaño_celda, gato_y * tamaño_celda,
                                (gato_x + 1) * tamaño_celda, (gato_y + 1) * tamaño_celda,
                                fill="orange", width=0)
        # Dibujar ratón (círculo gris pequeño)
        tamaño = tamaño_celda // 3  # Tamaño más pequeño para el ratón
        self.canvas.create_oval(raton_x * tamaño_celda + tamaño, raton_y * tamaño_celda + tamaño,
                                (raton_x + 1) * tamaño_celda - tamaño, (raton_y + 1) * tamaño_celda - tamaño,
                                fill="gray", width=0)

    def seleccionar_celda(self, evento):
        if self.turno_raton:
            x, y = self.raton_pos
            if evento.keysym == 'Left' and (x - 1, y) in self.movimientos_posibles(self.raton_pos):
                self.raton_pos = (x - 1, y)
            elif evento.keysym == 'Right' and (x + 1, y) in self.movimientos_posibles(self.raton_pos):
                self.raton_pos = (x + 1, y)
            elif evento.keysym == 'Up' and (x, y - 1) in self.movimientos_posibles(self.raton_pos):
                self.raton_pos = (x, y - 1)
            elif evento.keysym == 'Down' and (x, y + 1) in self.movimientos_posibles(self.raton_pos):
                self.raton_pos = (x, y + 1)
            self.dibujar_tablero()
            self.raiz.update()  # Actualiza la ventana para mostrar el movimiento
            if self.raton_pos == self.ruta_escape:
                self.mostrar_notificacion("El ratón ha escapado!")
                self.raiz.quit()
            else:
                self.turno_raton = False
                self.mover_gato()

#se encarga de calcular y encontrar el mejor movimiento usando minimax, actualiza la grafica para mostrar el movimiento, y verifica si el gato atrapo al raton
    def mover_gato(self):
        _, mejor_movimiento = self.minimax(self.tablero, self.gato_pos, self.raton_pos, 3, True)
        self.gato_pos = mejor_movimiento
        self.dibujar_tablero()
        self.raiz.update()  # Actualiza la ventana para mostrar el movimiento
        if self.gato_pos == self.raton_pos:
            self.mostrar_notificacion("¡El gato ha atrapado al ratón!")
            self.raiz.quit()
        else:
            self.turno_raton = True

    def evaluar_estado(self, gato_pos, raton_pos): #mediante manhattan sd calcula la distancia que hay entre el gato y el raton, y le pasa el valor a la distancia
        if gato_pos == raton_pos: #si en alguna ramificacion encuentra la mejor jugada y le doy prioridad al gato para atrapar al raton
            return float('inf')  # toma el valor infinito que es el valor maximo para mi gato
        distancia = abs(gato_pos[0] - raton_pos[0]) + abs(gato_pos[1] - raton_pos[1])
        return -distancia  # el resultado yo le voy a estar devolviendo a la funcion de evaluar

    def minimax(self, tablero, gato_pos, raton_pos, profundidad, max_jugador): #iter todos los movimientos del gato y descarta los movimiientos que no son posibles
        if gato_pos == raton_pos or profundidad == 0:
            return self.evaluar_estado(gato_pos, raton_pos), gato_pos # al terminar la recursividad, retorna la posicion calculada
        
        if max_jugador: #inicialmente mi raton es true
            max_eval = float('-inf')
            mejor_movimiento = gato_pos
            for mov in self.movimientos_posibles(gato_pos, exclude=[self.ruta_escape]): #crea las ramas
                eval, _ = self.minimax(tablero, mov, raton_pos, profundidad - 1, False) #llama sl minimax para la recursividad
                if eval > max_eval:
                    max_eval = eval
                    mejor_movimiento = mov
            return max_eval, mejor_movimiento
        else:
            min_eval = float('inf')#es turno del gato
            mejor_movimiento = raton_pos
            for mov in self.movimientos_posibles(raton_pos):
                eval, _ = self.minimax(tablero, gato_pos, mov, profundidad - 1, True) #cada vez que entra en recursividad la profundidad se resta -1
                if eval < min_eval:
                    min_eval = eval
                    mejor_movimiento = mov
            return min_eval, mejor_movimiento

    def movimientos_posibles(self, pos, exclude=[]):  #itera todos los movimientos del gato y descarta los movimiientos que no son posibles
        x, y = pos
        posibles = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nuevo_x, nuevo_y = x + dx, y + dy
            if 0 <= nuevo_x < len(self.tablero) and 0 <= nuevo_y < len(self.tablero): #verifica los movimientos posibles dentro del tablero
                if (nuevo_x, nuevo_y) not in exclude:
                    posibles.append((nuevo_x, nuevo_y)) #guarda los movimientos posibles
        return posibles

    def mostrar_notificacion(self, mensaje):
        tk.messagebox.showinfo("Fin del juego", mensaje)

if __name__ == "__main__":
    raiz = tk.Tk()
    juego = JuegoGatoRaton(raiz)
    raiz.mainloop()
