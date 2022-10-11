import itertools
import json
import pathlib
from pprint import pprint

TEST_STRUCTURE = {
    "separator": ".",
    "structure": {
        # "sections": {
        #     "project": ["project1", "project2"],
        "sections": {
            # "views": ["frontend", "backend", "model", "view"],
            # "routes": ["baseroutes", "v2routes"],
            "program": ["supervisor", "nginx"],
            # "resource": ["app", "api"],
            "env": ["dev", "test", "prod"],
            "sections": {"suffix": ["conf"]},
        },
        # },
    },
}


class Structure:
    def __init__(
        self,
        separator: str = None,
        structure: dict = None,
        sections: list[dict] = None,
        permutations: list[dict] = None,
        combinations: dict = None,
        string_groups: dict = None,
        tree_groups: dict = None,
    ):
        self._separator = separator
        self.structure = structure
        self.sections = sections
        self.permutations = permutations
        self.combinations = combinations
        self.string_groups = string_groups
        self.tree_groups = tree_groups

        if not self.structure:
            raise RuntimeError(
                "Incorrect data structure , no 'structure' key found.\n  Use `Structure(**data_dict)` or `Structure.from_json(json_string)` to load data."
            )
        self._build()

    def _build(self):
        self.sections = self._parse_sections(self.structure)
        self.permutations = self._permutations_from_sections(self.sections)
        self.combinations = self._create_combinations(self.permutations)
        self.string_groups = self._build_string_groups(self.combinations)
        self.tree_groups = self._build_tree_groups(self.string_groups)

    @property
    def separator(self):
        return self._separator

    @separator.setter
    def separator(self, sep):
        self._separator = sep
        self.string_groups = self._build_string_groups(self.combinations)
        self.tree_groups = self._build_tree_groups(self.string_groups)

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data))

    @classmethod
    def from_json_file(cls, file):
        with open(file, 'r') as jsonfile:
            return cls.from_json(jsonfile.read())

    # TODO: Fix for dictionary
    def to_json(self):
        return json.dumps(self)

    def save_to_json_file(self, file):
        with open(file, 'w') as json_file:
            json_file.write(self.to_json())

    def _parse_sections(self, structure: dict) -> list[dict]:
        struct_copy = structure.copy()

        sections = []

        def parse_section(section):
            deeper_section = section.pop('sections', None)
            sections.append(section)
            if deeper_section:
                parse_section(deeper_section)

        parse_section(struct_copy)
        return [s for s in sections if s]

    def _permutations_from_sections(self, sections) -> list[dict]:
        return [
            [{k: v for k, v in perm} for perm in list(itertools.permutations(section.items()))]
            for section in sections
        ]

    def _create_combinations(self, perm_dict_list):
        """
        Accepts list of dicts
        Each list item
        """
        combo_dict = {}
        for combo in itertools.product(*perm_dict_list):
            combined_dict = {}
            for d in combo:
                combined_dict.update(d)
            keys = combined_dict.keys()
            values = combined_dict.values()  # list of lists
            combinations = itertools.product(*values)
            combo_dict[tuple(keys)] = list(combinations)
        return combo_dict

    def _build_string_groups(self, combinations: dict) -> dict:
        return {
            self._separator.join(k): [self._separator.join(t) for t in v]
            for k, v in combinations.items()
        }

    def _build_tree_structure(self, section_sets, index=0):
        key_dict = dict.fromkeys(section_sets[index], {})
        if index < len(section_sets) - 1:
            index += 1
            next_dict = self._build_tree_structure(section_sets, index)
            for k in key_dict:
                key_dict[k] = next_dict
            return key_dict
        return key_dict

    def _build_tree_groups(self, string_groups):
        tree_groups = {}
        for name, group in string_groups.items():
            separated = [file.split(self.separator) for file in group]
            section_sets = list(set(z) for z in zip(*separated))
            tree_groups[name] = self._build_tree_structure(section_sets)
        return tree_groups

    # TODO: same as `print_string_groups` that will print all or accept a group to print
    def _create_tree_structure(self, tree_group: dict, prefix: str = ''):
        # prefix components
        SPACE = '    '
        BRANCH = '│   '
        # pointers
        TEE = '├── '
        LAST = '└── '
        # each section of tree group gets pointer ├── with a final └── :
        pointers = [TEE] * (len(tree_group) - 1) + [LAST]
        # print(f'{pointers=}')
        for pointer, section in zip(pointers, tree_group):
            yield prefix + pointer + section
            # print(f'{tree_group=}')
            if isinstance(tree_group.get(section), dict):  # extend the prefix and recurse:
                extension = BRANCH if pointer == TEE else SPACE
                # print(f'{extension=}')
                # i.e. SPACE because last, └── , above so no more |
                yield from self._create_tree_structure(
                    tree_group[section], prefix=prefix + extension
                )

    def create_directories(self, group: str, base_path: str = '.') -> None:
        if not (grp := self.string_groups.get(group)):
            return f'No group with structure: {group}'
        paths = [pathlib.Path(base_path, *section.split(self.separator)) for section in grp]
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)

    def create_files(self, group: str, base_path: str = '.') -> None:
        if not (grp := self.string_groups.get(group)):
            return f'No group with structure: {group}'
        for string in grp:
            pathlib.Path(base_path, string).touch()

    def display_string_groups(self, group=None):
        if not group:
            for k, v in self.string_groups.items():
                print(f"'{k}'")
                for item in v:
                    print(f'  {item}')
                print()
        else:
            if not (strings := self.string_groups.get(group)):
                return f'No group with structure: {group}'
            print(f"'{group}'")
            for item in strings:
                print(f'  {item}')

    def display_tree_groups(self, group=None):
        if not group:
            for name, tree in self.tree_groups.items():
                print(f"'{name}'")
                print()
                for line in self._create_tree_structure(tree):
                    print(line)
                print()
        else:
            if not (tree := self.tree_groups.get(group)):
                return f'No group with structure: {group}'
            print(f"'{group}'")
            print()
            for line in self._create_tree_structure(tree):
                print(line)

    def print_progression(self):
        print('STRUCTURE')
        print(self.structure)
        print()
        print('SECTIONS')
        print(self.sections)
        print()
        print('PERMUTATIONS')
        print(self.permutations)
        print()
        print('COMBINATIONS')
        for combination in self.combinations:
            print(combination)
        print()
        print('STRING GROUPS')
        print(self.display_string_groups())
        print()
        print('TREE GROUPS')
        print(self.display_tree_groups())


# TODO: Make TESTS
