import collections
from aioriak.datatypes.datatype import Datatype
from aioriak.datatypes import TYPES


class Set(collections.abc.Set, Datatype):
    '''A convergent datatype representing a Set with observed-remove
    semantics. Currently strings are the only supported value type.

    Example::
        myset.add('barista')
        myset.add('roaster')
        myset.add('brewer')

    Likewise they can simply be removed::
        myset.discard('barista')

    This datatype also implements the `Set ABC
    <https://docs.python.org/2/library/collections.html>`_, meaning it
    supports ``len()``, ``in``, and iteration.
    '''
    type_name = 'set'
    _type_error_msg = 'Sets can only be iterables of strings'

    def _post_init(self):
        self._adds = set()
        self._removes = set()

    def _default_value(self):
        return frozenset()

    def add(self, element):
        '''
        Adds an element to the set.

        .. note: You may add elements that already exist in the set.
           This may be used as an "assertion" that the element is a
           member.

        :param element: the element to add
        :type element: str
        '''
        self._check_element(element)
        self._adds.add(element)

    def discard(self, element):
        '''
        Removes an element from the set.

        .. note: You may remove elements from the set that are not
           present, but a context from the server is required.

        :param element: the element to remove
        :type element: str
        '''
        self._check_element(element)
        self._require_context()
        self._removes.add(element)

    def to_op(self):
        '''
        Extracts the modification operation from the set.

        :rtype: dict, None
        '''
        if not self._adds and not self._removes:
            return None
        changes = {}
        if self._adds:
            changes['adds'] = list(self._adds)
        if self._removes:
            changes['removes'] = list(self._removes)
        return changes

    @Datatype.modified.getter
    def modified(self):
        '''
        Whether this set has staged adds or removes.
        '''
        return len(self._removes | self._adds) > 0

    # collections.Set API, operates only on the immutable version
    def __contains__(self, element):
        return element in self.value

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def _coerce_value(self, new_value):
        return frozenset(new_value)

    def _check_type(self, new_value):
        if not isinstance(new_value, collections.abc.Iterable):
            return False
        for element in new_value:
            if not isinstance(element, str):
                return False
        return True

    @classmethod
    def _check_element(cls, element):
        if not isinstance(element, str):
            raise TypeError(Set._type_error_msg)

TYPES[Set.type_name] = Set
