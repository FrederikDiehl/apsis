__author__ = 'Frederik Diehl'

import uuid
from apsis.utilities.logging_utils import get_logger
import time

class Candidate(object):
    """
    A Candidate is a dictionary of parameter values, which should - or have
    been - evaluated.

    A Candidate object can be seen as a single iteration of the experiment.
    It is first generated as a suggestion of which parameter set to evaluate
    next, then updated with the result and cost of the evaluation.

    Attributes
    ----------

    id : uuid.UUID
        The uuid identifying this candidate. This is used to compare candidates
        over server and client borders.

    params : dict of string keys
        A dictionary of parameter value. The keys must correspond to the
        problem definition.
        The dictionary requires one key - and value - per parameter defined.

    result : float
        The results of evaluating the parameter set. This value is optimized
        over.

    failed : bool
        Whether the evaluation has been successful. Default is false.

    cost : float
        The cost of evaluating the parameter set. This may correspond to
        runtime, cost of ingredients or human attention required.

    worker_information : string
        This is worker-settable information which might be used for
        communicating things necessary for resuming evaluations et cetera. This
        is never touched in apsis.

    last_update_time : float
        The time the last update to this candidate happened.

    generated_time : float
        The time this candidate has been generated.
    """

    cand_id = None
    params = None
    result = None
    cost = None
    failed = None
    worker_information = None
    _logger = None

    last_update_time = None
    generated_time = None

    def __init__(self, params, cand_id=None, worker_information=None):
        """
        Initializes the unevaluated candidate object.

        Parameters
        ----------
        params : dict of string keys
            A dictionary of parameter value. The keys must correspond to the
            problem definition.
            The dictionary requires one key - and value - per parameter
            defined.
        cand_id : uuid.UUID, optional
            The uuid identifying this candidate. This is used to compare
            candidates over server and client borders.
            Note that this should only be set explicitly if you are
            instantiating an already known candidate with its already known
            UUID. Do not explicitly set the uuid for a new candidate!
        worker_information : string, optional
            This is worker-settable information which might be used for
            communicating things necessary for resuming evaluations et cetera.

        Raises
        ------
        ValueError
            Iff params is not a dictionary.
        """
        if cand_id is None:
            cand_id = uuid.uuid4().hex
        self.cand_id = cand_id
        self._logger = get_logger(self, extra_info="cand_id " + str(cand_id))
        self._logger.debug("Initializing new candidate. Params %s, cand_id %s,"
                           "worker_info %s", params, cand_id,
                           worker_information)

        if not isinstance(params, dict):
            self._logger.error("No parameter dict given, received %s instead",
                               params)
            raise ValueError("No parameter dictionary given, received %s "
                             "instead" %params)
        self.failed = False
        self.params = params
        self.worker_information = worker_information
        self.last_update_time = time.time()
        self.generated_time = time.time()
        self._logger.debug("Finished initializing the candidate.")

    def __eq__(self, other):
        """
        Compares two Candidate instances.

        Two Candidate instances are defined as being equal iff their ids
        are equal. A non-Candidate instance is never equal to a
        Candidate.

        Parameters
        ----------
        other :
            The object to compare this Candidate instance to.

        Returns
        -------
        equality : bool
            True iff other is a Candidate instance and their ids are equal.
        """
        self._logger.debug("Comparing candidates self (%s) with %s.", self,
                           other)
        if not isinstance(other, Candidate):
            equality = False
        elif self.cand_id == other.cand_id:
            equality = True
        else:
            equality = False
        self._logger.debug("Equality: %s", equality)
        return equality

    def __str__(self):
        """
        Stringifies this Candidate.

        A stringified Candidate is the stringified form of its dict.

        Returns
        -------
        string : string
            The stringified Candidate.

        """
        cand_dict = self.to_dict(do_logging=False)
        string = str(cand_dict)
        return string

    def to_dict(self, do_logging=True):
        """
        Converts this candidate to a dictionary.

        Returns
        -------
        d : dictionary
            Contains the following key/value pairs:
            "id" : string
                The id of the candidate.
            "params" : dict
                This dictionary contains one entry for each parameter,
                each with the string name as key and the value as value.
            "result" : float or None
                The result of the Candidate
            "failed" : bool
                Whether the evaluation failed.
            "cost" : float or None
                The cost of evaluating the Candidate
            "worker_information" : any jsonable or None
                Client-settable worker information.
        """
        if do_logging:
            self._logger.debug("Converting cand to dict.")
        d = {"cand_id": self.cand_id,
             "params": self._param_defs_to_dict(do_logging=do_logging),
             "result": self.result,
             "failed": self.failed,
             "cost": self.cost,
             "last_update_time": self.last_update_time,
             "generated_time": self.generated_time,
             "worker_information": self.worker_information}
        if do_logging:
            self._logger.debug("Generated dict %s", d)
        return d

    def _param_defs_to_dict(self, do_logging=True):
        """
        Returns a parameter definition dictionary representation.

        Returns
        -------
        d : dict
            Dictionary of the parameters.
        """
        if do_logging:
            self._logger.debug("Converting param_def to dict.")
        d = {}
        for k in self.params.keys():
            d[k] = self.params[k]
        if do_logging:
            self._logger.debug("param_def dict is %s", d)
        return d


def from_dict(d):
    """
    Builds a new candidate from a dictionary.

    Parameters
    ----------
    cand_dict : dictionary
        Uses the same format as in Candidate.to_dict.

    Returns
    -------
    c : Candidate
        The corresponding candidate.
    """
    cand_logger = get_logger("models.Candidate")
    cand_logger.log(5, "Constructing new candidate from dict %s.", d)
    cand_id = None
    if "cand_id" in d:
        cand_id = d["cand_id"]
    c = Candidate(d["params"], cand_id=cand_id)
    c.result = d.get("result", None)
    c.cost = d.get("cost", None)
    c.failed = d.get("failed", False)
    c.last_update_time = d.get("last_update_time")
    c.generated_time = d.get("generated_time")
    c.worker_information = d.get("worker_information", None)
    cand_logger.log(5, "Constructed candidate is %s", c)
    return c
