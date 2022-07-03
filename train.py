import random
import numpy as np
import time
import csv
from tqdm import tqdm

from genetic_ai import Genetic_AI
from pytris import Pytris

def cross(a1, a2):
    """
    Compute crossover of two agents, returning a new agent
    """
    new_genotype = []
    a1_prop = a1.fit_rel / a2.fit_rel
    for i in range(len(a1.genotype)):
        rand = random.uniform(0, 1)
        if rand > a1_prop:
            new_genotype.append(a1.genotype[i])
        else:
            new_genotype.append(a2.genotype[i])

    return Genetic_AI(genotype=np.array(new_genotype), mutate=True)


def compute_fitness(agent, num_trials):
    """
    Given an agent and a number of trials, computes fitness as
    arithmetic mean of lines cleared over the trials
    """
    fitness = []
    for _ in range(num_trials):
        pytris = Pytris(ai=agent, headless=True)
        score = pytris.run_headless()
        fitness.append(score)
    return np.average(np.array(fitness))



def run(num_epochs=20, num_trials=3, pop_size=100, num_elite=5, survival_rate=.35, logging_file=f"run_at_{int(time.time())}.csv"):

    # data collection over epochs
    headers = ['avg_fit','avg_gene', 'top_fit', 'top_gene', 'elite_fit', 'elite_gene']
    data=[1, np.ones(9).tolist(), 1, np.ones(9).tolist(),  1, np.ones(9).tolist()]
    with open(logging_file, 'w+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(data)

    # create inital population
    population = [Genetic_AI() for _ in range(pop_size)]

    for epoch in tqdm(range(num_epochs), desc="Epochs passed", unit="epochs"):
        """
        Fitness
        """

        # data collection within epochs
        total_fitness = 0
        top_agent = 0
        gene_sum = np.zeros(9)

        for i, agent in tqdm(enumerate(population), desc="Agents computed", unit=" agents"):
            # compute fitness, add to total
            agent.fit_score = compute_fitness(agent, num_trials=num_trials)
            total_fitness += agent.fit_score 
            gene_sum+=agent.genotype


        # compute % of fitness accounted for by each agent
        for agent in population:
            agent.fit_rel = agent.fit_score / total_fitness

        """
        Selection
        """

        next_gen = []

        # sort population by descending fitness
        sorted_pop = sorted(population, reverse=True)

        # elite selection: copy over genotypes from top preforming agents
        elite_fit_score = 0
        elite_genes = np.zeros(9)
        top_agent=sorted_pop[0]

        for i in range(num_elite):
            elite_fit_score +=sorted_pop[i].fit_score
            elite_genes += sorted_pop[i].genotype
            next_gen.append(Genetic_AI(genotype=sorted_pop[i].genotype, mutate=False))

        # selection: select top agents as parents base on survival rate
        num_parents = round(pop_size * survival_rate)
        parents = sorted_pop[:num_parents]

        # crossover: randomly select 2 parents and cross genotypes
        for _ in range(pop_size-(num_elite)):
            # randomly select parents, apply crossover, and add to the next generation
            # the cross functions automatically applies mutation to the new agent
            parents = random.sample(parents, 2)
            next_gen.append(cross(parents[0], parents[1]))


        avg_fit = (total_fitness/pop_size)
        avg_gene = (gene_sum/pop_size)
        top_fit = (top_agent.fit_score)
        top_gene = (top_agent.genotype)
        elite_fit = (elite_fit_score/num_elite)
        elite_gene = (elite_genes/num_elite)

        data = [avg_fit, avg_gene.tolist(), top_fit, top_gene.tolist(), elite_fit, elite_gene.tolist()]
        with open(logging_file, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)

        print(f'{epoch=}\ttotal fitness={total_fitness/pop_size}\tbest agent={top_agent.fit_score}')

        population = next_gen

    return data

if __name__ == '__main__':
    run()
        