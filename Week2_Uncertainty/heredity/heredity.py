import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probInformation = getJointDistInfo(people, one_gene, two_genes, have_trait)
    joint_probability = 1

    for person in people:
        joint_probability *= findProb(person, people, probInformation)

    return joint_probability


def findProb(person, people, jointProbInfo):
    jointProb = 0

    # Info about the person for whom we want to find the probability
    personGene = jointProbInfo[person][0]
    existsTrait = jointProbInfo[person][1]

    # If they have parents, they will be stored here
    p1 = people[person]["mother"]
    p2 = people[person]["father"]

    # If the person doesn't have parents, calculate probabilites based on info in PROBS
    if p1 == None and p2 == None:
        jointProb = PROBS["gene"][personGene] * PROBS["trait"][personGene][existsTrait]
    else:
        # Person can get 1 copy of the gene from parent1 or from parent2 but not both
        if personGene == 1:
            # p1Prob represents the probability that person will get 1 copy of the gene from p1
            if jointProbInfo[p1][0] == 1:
                p1Prob = 0.5
            elif jointProbInfo[p1][0] == 2:
                p1Prob = 1 - PROBS["mutation"]
            else:
                p1Prob = PROBS["mutation"]
            
            # p2Prob represents the probability that person will get 1 copy of the gene from p2
            if jointProbInfo[p2][0] == 1:
                p2Prob = 0.5
            elif jointProbInfo[p2][0] == 2:
                p2Prob = 1 - PROBS["mutation"]
            else:
                p2Prob = PROBS["mutation"] 

            # Probability of existsTrait given 1 copy of the gene
            traitPossibility = PROBS["trait"][1][existsTrait]
            # If p1Prob is 0.01 for example, the chances of p1Prob not happening is 1 - p1Prob
            jointProb = traitPossibility * (p1Prob * (1 - p2Prob) + p2Prob * (1 - p1Prob))

        elif personGene == 2:
            # p1Prob represents the probability that person will get 2 copies of the gene from p1
            if jointProbInfo[p1][0] == 1:
                p1Prob = 0.5
            elif jointProbInfo[p1][0] == 2:
                p1Prob = 1 - PROBS["mutation"]
            else:
                p1Prob = PROBS["mutation"]
            
            # p2Prob represents the probability that person will get 2 copies of the gene from p2
            if jointProbInfo[p2][0] == 1:
                p2Prob = 0.5
            elif jointProbInfo[p2][0] == 2:
                p2Prob = 1 - PROBS["mutation"]
            else:
                p2Prob = PROBS["mutation"] 

            # Probability of existsTrait given 2 copies of the gene
            traitPossibility = PROBS["trait"][2][existsTrait]
            # Joint probability of both parents 
            jointProb = traitPossibility * p1Prob * p2Prob

        else:
            # p1Prob represents the probability that person will get 0 copies of the gene from p1
            if jointProbInfo[p1][0] == 1:
                p1Prob = 0.5
            elif jointProbInfo[p1][0] == 2:
                p1Prob = 1 - PROBS["mutation"]
            else:
                p1Prob = PROBS["mutation"]
            
            # p2Prob represents the probability that person will get 0 copies of the gene from p2
            if jointProbInfo[p2][0] == 1:
                p2Prob = 0.5
            elif jointProbInfo[p2][0] == 2:
                p2Prob = 1 - PROBS["mutation"]
            else:
                p2Prob = PROBS["mutation"] 

            # Probability of existsTrait given 0 copies of the gene
            traitPossibility = PROBS["trait"][0][existsTrait]
            # Joint probability of both parents 
            jointProb = traitPossibility * p1Prob * p2Prob

    return jointProb


def getJointDistInfo(people, one_gene, two_genes, have_trait):
    probInformation = dict()

    for person in people:
        if person in one_gene:
            if person in have_trait:
                probInformation[person] = [1, True]
            else:
                probInformation[person] = [1, False]
        elif person in two_genes:
            if person in have_trait:
                probInformation[person] = [2, True]
            else:
                probInformation[person] = [2, False]
        else:
            if person in have_trait:
                probInformation[person] = [0, True]
            else:
                probInformation[person] = [0, False]

    return probInformation


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    probInformation = getJointDistInfo(probabilities.keys(), one_gene, two_genes, have_trait)

    for person in probInformation:
        personGene = probInformation[person][0]
        personTrait = probInformation[person][1]

        probabilities[person]["gene"][personGene] += p
        probabilities[person]["trait"][personTrait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    
    for person in probabilities:
        sumOfGenes = 0
        for i in range(3):
            sumOfGenes += probabilities[person]["gene"][i]

        geneScale = 1 / sumOfGenes
        
        for i in range(3):
            probabilities[person]["gene"][i] *= geneScale

        sumOfTraits = probabilities[person]["trait"][0] + probabilities[person]["trait"][1]
        traitScale = 1 / sumOfTraits

        for i in range(2):
            probabilities[person]["trait"][i] *= traitScale
if __name__ == "__main__":
    main()
