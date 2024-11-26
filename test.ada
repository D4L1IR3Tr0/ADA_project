make personne:
    string nom
    int age
/.

define estmajeur(personne x):
    bool retour
    if(x.age >= 18):
        retour <- true
    else:
        retour <- false
    /.
    write(retour)
/.

personne dali
dali.nom <- "dali"
dali.age <- 17
estmajeur(dali)
