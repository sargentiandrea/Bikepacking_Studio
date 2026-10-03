"""
Gestore del ciclo di vita di UN worker in background alla volta.

Prima i tre flussi del pannello (altimetria, nomi dei luoghi, superfici)
ripetevano lo stesso codice: ognuno aveva il proprio worker, la lista di
sopravvivenza, la richiesta in sospeso e il token. Ora vivono qui, in un solo
punto, così una correzione al ciclo di vita vale per tutti e tre.

Questo modulo NON importa Qt: usa solo i metodi dei worker (QThread) che
servono davvero: isRunning, request_stop, start, deleteLater e il segnale
con il risultato. Si può quindi provare anche con worker finti.
"""


class GestoreWorkerSingolo:
    """
    Fa girare un worker alla volta per un certo compito.

    - Se arriva una nuova richiesta mentre il worker lavora, la richiesta
      va "in sospeso" e il vecchio worker viene fermato: la nuova parte appena
      il vecchio ha finito (ne resta in sospeso solo una, l'ultima).
    - Ogni richiesta incrementa un "token": un risultato con un token vecchio
      è superato (es. l'utente ha cambiato percorso) e viene scartato.
    - I worker vivi restano in una lista di sopravvivenza finché non finiscono
      davvero: perdere il riferimento a un thread attivo fa crashare Qt.
    """

    def __init__(self, crea_worker, nome_segnale, alla_fine):
        """
        - crea_worker(richiesta): costruisce il worker per quella richiesta
        - nome_segnale: nome del segnale del worker che porta il risultato
          (es. "altimetria_pronta")
        - alla_fine(risultato): chiamata col risultato SOLO se è ancora attuale
        """
        self._crea_worker = crea_worker
        self._nome_segnale = nome_segnale
        self._alla_fine = alla_fine
        self.worker = None
        self.attivi = []  # tiene in vita i worker finché non finiscono davvero
        self.in_sospeso = None
        self.token = 0

    def richiedi(self, richiesta):
        """
        Registra una nuova richiesta (token + 1). Se un worker sta ancora
        lavorando la mette in coda e gli chiede di fermarsi; altrimenti
        avvia subito il nuovo worker.
        """
        self.token += 1

        try:
            ancora_attivo = self.worker is not None and self.worker.isRunning()
        except RuntimeError:
            # Difesa: se il riferimento non è stato azzerato in tempo, il worker
            # va trattato come già finito invece di bloccare tutto il pannello.
            ancora_attivo = False
            self.worker = None

        if ancora_attivo:
            self.in_sospeso = richiesta
            # La richiesta precedente è superata: meglio fermarla subito che
            # lasciarla girare a vuoto (con percorsi enormi durava minuti).
            self.worker.request_stop()
            return

        self._avvia(richiesta)

    def invalida(self):
        """
        Rende superati i risultati in arrivo (token + 1) e chiede al worker
        eventualmente in corso di fermarsi. Serve al cambio di percorso: un
        risultato tardivo non deve ripopolare campi appena svuotati.
        """
        self.token += 1
        if self.worker is not None:
            try:
                self.worker.request_stop()
            except RuntimeError:
                pass  # il thread è già stato distrutto: niente da fermare

    def _avvia(self, richiesta):
        """Crea e fa partire il worker, legandolo al token corrente."""
        token_corrente = self.token
        worker = self._crea_worker(richiesta)
        self.worker = worker
        self.attivi.append(worker)
        getattr(worker, self._nome_segnale).connect(
            lambda risultato, token=token_corrente: self._fine(risultato, token)
        )
        worker.finished.connect(lambda worker=worker: self._ripulisci(worker))
        worker.start()

    def _ripulisci(self, worker):
        """Toglie dalla lista di sopravvivenza un worker finito e lo elimina.

        Riavvia anche la richiesta in coda: `finished` arriva comunque, anche
        se il worker è uscito senza emettere il segnale di risultato (perché
        annullato, o perché è saltata un'eccezione). Senza questo, la coda
        resterebbe bloccata per sempre e l'interfaccia inutilizzabile.
        """
        if worker in self.attivi:
            self.attivi.remove(worker)
        if self.worker is worker:
            # Fondamentale: senza azzerare il riferimento, il prossimo isRunning()
            # punterebbe a un thread distrutto ("Internal C++ object already deleted").
            self.worker = None
        worker.deleteLater()
        self._riavvia_in_coda()

    def _riavvia_in_coda(self):
        """Avvia la richiesta in attesa se non c'è più nessun worker attivo."""
        if self.in_sospeso is None or self.worker is not None:
            return
        in_sospeso = self.in_sospeso
        self.in_sospeso = None
        self._avvia(in_sospeso)

    def _fine(self, risultato, token):
        """Un worker ha finito: avvia l'eventuale richiesta in coda, poi consegna il risultato se è attuale."""
        # La coda viene svuotata da _ripulisci(), agganciata a `finished`, che
        # arriva sempre. Qui non si avvia nulla, per non partire due volte.
        if token != self.token:
            return  # nel frattempo l'utente ha cambiato percorso: risultato superato
        self._alla_fine(risultato)
