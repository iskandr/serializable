# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function, division, absolute_import

from .helpers import (
    from_serializable_repr,
    to_serializable_repr,
    to_json,
    from_json,
)

class Serializable(object):
    """
    Base class for all PyEnsembl objects which provides default
    methods such as to_json, from_json, __reduce__, and from_dict

    Relies on the following condition:
         (1) a user-defined to_dict method
         (2) the keys of to_dict() must match the arguments to __init__
    """

    def __str__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join("%s=%s" % (k, v) for (k, v) in self.to_dict().items()))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.to_dict() == other.to_dict()

    def to_dict(self):
        """
        Derived classes must implement this method and return a dictionary
        whose keys match the parameters to __init__. The values must be
        primitive atomic types (bool, string, int, float), primitive
        collections (int, list, tuple) or instances of Serializable.
        """
        raise NotImplementedError("Method to_dict() not implemented for %s" % (
            self.__class__.__name__,))

    def __hash__(self):
        return hash(tuple(sorted(self.to_dict().items())))

    @classmethod
    def _reconstruct_nested_objects(cls, state_dict):
        """
        Nested serializable objects will be represented as dictionaries so we
        allow manual reconstruction of those objects in this method.

        By default just returns the state dictionary unmodified.
        """
        return state_dict

    @classmethod
    def from_dict(cls, state_dict):
        """
        Given a dictionary of flattened fields (result of calling to_dict()),
        returns an instance.
        """
        state_dict = cls._reconstruct_nested_objects(state_dict)
        return cls(**state_dict)

    def to_json(self):
        """
        Returns a string containing a JSON representation of this Genome.
        """
        return to_json(self)

    @classmethod
    def from_json(cls, json_string):
        """
        Reconstruct an instance from a JSON string.
        """
        return from_json(json_string)

    def write_json_file(self, path):
        """
        Serialize this VariantCollection to a JSON representation and write it
        out to a text file.
        """
        with open(path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def read_json_file(cls, path):
        """
        Construct a VariantCollection from a JSON file.
        """
        with open(path, 'r') as f:
            json_string = f.read()
        return cls.from_json(json_string)

    def __reduce__(self):
        """
        Overriding this method directs the default pickler to reconstruct
        this object using our from_dict method.
        """

        # I wish I could just return (self.from_dict, (self.to_dict(),) but
        # Python 2 won't pickle the class method from_dict so instead have to
        # use globally defined functions.
        return (from_serializable_repr, (to_serializable_repr(self),))
