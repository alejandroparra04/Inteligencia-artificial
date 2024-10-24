

from logic import *

lluvia = Symbol("lluvia")
bbc = Symbol("bbc")
unimayor = Symbol("unimayor")    #explicacion del codigo

knowledge = And(
    Implication(Not(lluvia), bbc),  # si no llueve, los estudiantes visitan a BBC hoy.
    Or(bbc, unimayor),              # Visitan BBC o Unimayor, pero no ambos.
    Not(And(bbc, unimayor)),        # No ambos.
    unimayor                        # Estudiantes visitaron Unimayor hoy.
)

print(model_check(knowledge, lluvia))  # que se puede inferir acerca de la lluvia.
print(model_check(knowledge, bbc))     # que se puede inferir acerca de la visita a BBC.
