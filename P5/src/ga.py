import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

width = 200
height = 16

options = [
    "-",  # an empty space
    "X",  # a solid wall
    "?",  # a question mark block with a coin
    "M",  # a question mark block with a mushroom
    "B",  # a breakable block
    "o",  # a coin
    "|",  # a pipe segment
    "T",  # a pipe top
    "E",  # an enemy
    #"f",  # a flag, do not generate
    #"v",  # a flagpole, do not generate
    #"m"  # mario's start position, do not generate
]

# The level as a grid of tiles


class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients))
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    # Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!
    def mutate(self, genome):
        # STUDENT implement a mutation operator, also consider not mutating this individual
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc

        left = 4
        right = width - 1
        pipe_height_limit = int(height * 0.8)
        for y in range(height):
            for x in range(left, right):
                #if random number, mutate to select random tile from options
                # weight the different tile types so it's not uniformly random

                if random.random() < 0.6:
                    choice = random.choices(options, weights=[0.45, 0.1, 0.05, 0.05, 0.1, 0.05, 0, 0.05, 0.05], k=1)[0]

                    # if the adjacent tile is a breakable block, a question block, or a wall, adjust choice to favor more blocks
                    if x > left and genome[y][x-1] in ["B", "M", "?", "X"]:
                        choice = random.choices(options, weights=[0.1, 0.10, 0.2, 0.2, 0.35, 0.05, 0, 0, 0], k=1)[0]

                    if y < pipe_height_limit and choice in ["T", "|"]:
                        choice = "-"

                    if y == height - 1:
                        if random.random() < 0.1:
                            choice = "-"
                        else:
                            choice = "X"

                    # if height is between height - 1 and height * 0.8, and the choice is a wall, brick, or question block, change it to empty space
                    if y < height - 1 and y > pipe_height_limit and choice in ["X", "B", "M", "?"]:
                        choice = "-"

                    # if choice is an Enemy, check if there is a platform below it, if not, change it to empty space
                    if choice == "E":
                        if y < height - 1 and genome[y+1][x] not in ["X", "B", "M", "?"]:
                            choice = "-"

                    # Delete everything above a certain height
                    if y < height * 0.1:
                        choice = "-"

                    genome[y][x] = choice

        return genome

    # Create zero or more children from self and other
    def generate_children(self, other):
        # crossover
        new_genome = copy.deepcopy(self.genome)
        # if you want to return more genomes, add new genome variable

        # Leaving first and last columns alone...
        # do crossover with other
        left = 1
        right = width - 1
        pipe_height_limit = int(height * 0.8)

        split_point = random.randint(left, right)

        for y in range(height):
            for x in range(left, right):
                # STUDENT Which one should you take?  Self, or other?  Why?
                # STUDENT consider putting more constraints on this to prevent pipes in the air, etc

                # Split Point at random

                if x < split_point:
                    new_genome[y][x] = other.genome[y][x]

        # mutate the new genomes
        new_genome = self.mutate(new_genome)

        for y in range(height):
            for x in range(left, right):
                # Erase all pipes above 80% of the level
                if y < pipe_height_limit and new_genome[y][x] in ["T", "|"]:
                    new_genome[y][x] = "-"

                # Erase all weird tiles at the mario spawn
                if x < 4 or x > width - 3 and new_genome[y][x] in ["T", "|", "B", "M", "?", "E"]:
                    new_genome[y][x] = "-"

                # Delete all pipe segments that are not connected to a pipe top
                if new_genome[y][x] == "|":
                    connected = False
                    for y2 in range(pipe_height_limit, y):
                        if new_genome[y2][x] == "T":
                            connected = True
                            break
                    if not connected:
                        # loop through the column and delete all pipe segments
                        for y2 in range(pipe_height_limit, height):
                            if new_genome[y2][x] == "|":
                                new_genome[y2][x] = "-"


                # Complete all generated pipes and delete all pipes above the pipe exit. Make sure there's 2 walkable spaces above the pipe exit
                if new_genome[y][x] == "T":
                    for y2 in range(y+1, height):
                        new_genome[y2][x] = "|"
                    for y2 in range(0, y):
                        if new_genome[y2][x] == "|":
                            new_genome[y2][x] = "-"
                    new_genome[y - 1][x] = random.choice(["-", "o"])
                    new_genome[y - 2][x] = random.choice(["-", "o"])
                    new_genome[y - 3][x] = "-"
                    new_genome[y - 1][x + 1] = random.choice(["-", "o"])
                    new_genome[y - 2][x + 1] = random.choice(["-", "o"])

                # if the block is a breakable block or a coin, and the ground beneath it is over 5 tiles away, it can't be reached by Mario, so change it to empty space.
                # if the ground beneath it is just under 2 tiles away, Mario can't fit under it, so change it to empty space.
                    
                if y < height - 1 and new_genome[y][x] in ["B", "?", "M", "X", "o"]:
                    count = 0
                    for y2 in range(y + 1, height):
                        count += 1
                        if new_genome[y2][x] in ["X", "B", "M", "?", "T", "E"]:
                            break
                    if count > 5 or count < 3:
                        new_genome[y][x] = "-"
                    elif count < 4 and new_genome[y][x] in ["X", "?", "M"]:
                        new_genome[y][x] = "-"

                # if the tile is an enemy, check if there is a platform below it, if not, change it to empty space
                if new_genome[y][x] == "E":
                    if y < height - 1 and new_genome[y+1][x] not in ["X", "B", "M", "?"]:
                        new_genome[y][x] = "-"

                # Delete lone blocks
                if new_genome[y][x] in ["X", "B", "M", "?"]:
                    if x > 1 and x < width - 2:
                        if new_genome[y][x-1] in ["-", "o"] and new_genome[y][x+1] in ["-", "o"]:
                            new_genome[y][x] = "-"

                # Check for gaps in the floor, if they are too wide, fill in a block
                if y == height - 1 and new_genome[y][x] == "-":
                    count = 0
                    for x2 in range(x, width):
                        count += 1
                        if new_genome[y][x2] not in ["-", "o"]:
                            break
                    if count > 3:
                        new_genome[y][x + 3] = "X"

                # Delete everything above a certain height
                if y < height * 0.1:
                    new_genome[y][x] = "-"

                

        # do mutation; note we're returning a one-element tuple here

        return ({Individual_Grid(new_genome)})

    # Turn the genome into a level string (easy for this genome)
    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        # changed -1 to -2 to make flagpole one block away from the edge
        
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        g = [random.choices(options, k=width) for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        g[8:14][-1] = ["f"] * 6
        g[14:16][-1] = ["X", "X"]
        return cls(g)


def offset_by_upto(val, variance, min=None, max=None):
    val += random.normalvariate(0, variance**0.5)
    if min is not None and val < min:
        val = min
    if max is not None and val > max:
        val = max
    return int(val)


def clip(lo, val, hi):
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val

# Inspired by https://www.researchgate.net/profile/Philippe_Pasquier/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000.pdf


class Individual_DE(object):
    # Calculating the level isn't cheap either so we cache it too.
    __slots__ = ["genome", "_fitness", "_level"]

    # Genome is a heapq of design elements sorted by X, then type, then other parameters
    def __init__(self, genome):
        self.genome = list(genome)
        heapq.heapify(self.genome)
        self._fitness = None
        self._level = None

    # Calculate and cache fitness
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Add more metrics?
        # STUDENT Improve this with any code you like
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        penalties = 0
        # STUDENT For example, too many stairs are unaesthetic.  Let's penalize that
        if len(list(filter(lambda de: de[1] == "6_stairs", self.genome))) > 5:
            penalties -= 2

        # add penalty for too many or too few enemies
        enemy_count = len(list(filter(lambda de: de[1] == "2_enemy", self.genome)))
        if enemy_count > 15: penalties -= enemy_count - 15  # Penalize for each enemy above 15 
        if enemy_count < 5: penalties -= 5 - enemy_count  # Penalize for each enemy below 5

        # STUDENT If you go for the FI-2POP extra credit, you can put constraint calculation in here too and cache it in a new entry in __slots__.
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients)) + penalties
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, new_genome):
        # STUDENT How does this work?  Explain it in your writeup.
        # STUDENT consider putting more constraints on this, to prevent generating weird things
        pipe_height_limit = int(height * 0.8)
        if random.random() < 0.1 and len(new_genome) > 0:
            to_change = random.randint(0, len(new_genome) - 1)
            de = new_genome[to_change]
            new_de = de
            x = de[0]
            de_type = de[1]
            choice = random.random()

            stairs_positions = [de[0] for de in new_genome if de[1] == '6_stairs']

            def is_too_close_to_stairs(x):
                return any(abs(x - stairs_x) <= 2 for stairs_x in stairs_positions)
            
            if de_type in ["4_block", "5_qblock"]:
                y = de[2]
                break_power = de[3]

                if is_too_close_to_stairs(x):
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)

                if y > pipe_height_limit:
                    y = offset_by_upto(y, height / 3, min=1, max=pipe_height_limit)

                if choice > 0.5:
                    break_power = not de[3]
                
                new_de = (x, de_type, y, break_power)

            elif de_type == "1_platform":
                w = de[2]
                y = de[3]
                madeof = de[4]

                if is_too_close_to_stairs(x + w):
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                
                if y > pipe_height_limit:
                    y = offset_by_upto(y, height / 2, min=1, max=pipe_height_limit)

                if choice > 0.5:
                    madeof = random.choice(["?", "X", "B"])
                
                new_de = (x, de_type, w, y, madeof)

            elif de_type == "7_pipe":
                h = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    h = offset_by_upto(h, 2, min=2, max=pipe_height_limit)
                
                new_de = (x, de_type, h)           

            elif de_type == "3_coin":
                y = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    y = offset_by_upto(y, height / 2, min=0, max=pipe_height_limit)
                
                new_de = (x, de_type, y)

            elif de_type == "0_hole":
                w = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 12, min=1, max=width - 2)
                else:
                    w = offset_by_upto(w, 4, min=1, max=width - 2)
                new_de = (x, de_type, w)

            elif de_type == "6_stairs":
                h = de[2]
                dx = de[3]  # -1 or 1
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    h = offset_by_upto(h, 8, min=1, max=pipe_height_limit)
                else:
                    dx = -dx if dx == 1 else 1  # Ensure dx remains valid (-1 or 1)

                if h > pipe_height_limit:
                    h = random.randint(0, pipe_height_limit)
                
                new_de = (x, de_type, h, dx)

            elif de_type == "2_enemy":
                # No mutation logic specified for enemies.
                pass

            # Replace the old gene with the new one
            new_genome.pop(to_change)
            heapq.heappush(new_genome, new_de)

        return new_genome
    
    def generate_children(self, other):
        # STUDENT How does this work?  Explain it in your writeup.
        pa = random.randint(0, len(self.genome) - 1)
        pb = random.randint(0, len(other.genome) - 1)
        a_part = self.genome[:pa] if len(self.genome) > 0 else []
        b_part = other.genome[pb:] if len(other.genome) > 0 else []
        ga = a_part + b_part
        b_part = other.genome[:pb] if len(other.genome) > 0 else []
        a_part = self.genome[pa:] if len(self.genome) > 0 else []
        gb = b_part + a_part
        # do mutation
        return Individual_DE(self.mutate(ga)), Individual_DE(self.mutate(gb))

    # Apply the DEs to a base level.
    def to_level(self):
        if self._level is None:
            base = Individual_Grid.empty_individual().to_level()
            for de in sorted(self.genome, key=lambda de: (de[1], de[0], de)):
                # de: x, type, ...
                x = de[0]
                de_type = de[1]
                if de_type == "4_block":
                    y = de[2]
                    breakable = de[3]
                    base[y][x] = "B" if breakable else "X"
                elif de_type == "5_qblock":
                    y = de[2]
                    has_powerup = de[3]  # boolean
                    base[y][x] = "M" if has_powerup else "?"
                elif de_type == "3_coin":
                    y = de[2]
                    base[y][x] = "o"
                elif de_type == "7_pipe":
                    h = de[2]
                    base[height - h - 1][x] = "T"
                    for y in range(height - h, height):
                        base[y][x] = "|"
                elif de_type == "0_hole":
                    w = de[2]
                    for x2 in range(w):
                        base[height - 1][clip(1, x + x2, width - 2)] = "-"
                elif de_type == "6_stairs":
                    h = de[2]
                    dx = de[3]  # -1 or 1
                    for x2 in range(1, h + 1):
                        for y in range(x2 if dx == 1 else h - x2):
                            base[clip(0, height - y - 1, height - 1)][clip(1, x + x2, width - 2)] = "X"
                elif de_type == "1_platform":
                    w = de[2]
                    h = de[3]
                    madeof = de[4]  # from "?", "X", "B"
                    for x2 in range(w):
                        base[clip(0, height - h - 1, height - 1)][clip(1, x + x2, width - 2)] = madeof
                elif de_type == "2_enemy":
                    base[height - 2][x] = "E"
            self._level = base
        return self._level

    @classmethod
    def empty_individual(_cls):
        # STUDENT Maybe enhance this
        g = []
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # STUDENT Maybe enhance this
        elt_count = random.randint(8, 128)
        g = [random.choice([
            (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
            (random.randint(1, width - 2), "1_platform", random.randint(1, 8), random.randint(0, height - 1), random.choice(["?", "X", "B"])),
            (random.randint(1, width - 2), "2_enemy"),
            (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
            (random.randint(1, width - 2), "4_block", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "5_qblock", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "6_stairs", random.randint(1, height - 4), random.choice([-1, 1])),
            (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 4))
        ]) for i in range(elt_count)]
        return Individual_DE(g)


Individual = Individual_DE


def generate_successors(population):
    results = []
    # STUDENT Design and implement this
    # Hint: Call generate_children() on some individuals and fill up results.
    
    fittest_individuals = sorted(population, key=Individual.fitness, reverse=True)

    # cut off the bottom 90% of fittest_individuals
    fittest_individuals = fittest_individuals[:int(len(fittest_individuals) * 0.1)]

    # generate as many children as there are parents

    for _ in range(len(population) - len(fittest_individuals)):
        parent1 = random.choice(fittest_individuals)
        while not parent1.genome:
            parent1 = random.choice(fittest_individuals)
        parent2 = random.choice(fittest_individuals)
        while parent1 == parent2 or not parent2.genome:
            parent2 = random.choice(fittest_individuals)
        results.extend(parent1.generate_children(parent2))

    # add the fittest individuals to the results
    results.extend(fittest_individuals)

    return results


def ga():
    #individuals are whole levels

    # STUDENT Feel free to play with this parameter
    pop_limit = 480
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " + str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        population = [Individual.random_individual() if random.random() < 0.9
                      else Individual.empty_individual()
                      for _g in range(pop_limit)]
        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)
        init_done = time.time()
        print("Created and calculated initial population statistics in:", init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    best = max(population, key=Individual.fitness)
                    print("Generation:", str(generation))
                    print("Max fitness:", str(best.fitness()))
                    print("Average generation time:", (now - start) / generation)
                    print("Net time:", now - start)
                    with open("levels/last.txt", 'w') as f:
                        for row in best.to_level():
                            f.write("".join(row) + "-" + "\n")
                generation += 1
                # STUDENT Determine stopping condition
                stop_condition = False
                if stop_condition:
                    break
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(Individual.calculate_fitness,
                                           next_population,
                                           batch_size)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    print("Best genome: " + str(best.genome))
    now = time.strftime("%m_%d_%H_%M_%S")
    # STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 10):
        with open("levels/" + now + "_" + str(k) + ".txt", 'w') as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "-" + "\n")