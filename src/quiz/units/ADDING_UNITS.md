# Adding a New Quiz Unit

This guide describes how to add a new quiz unit to the system.

## Steps

1. **Create a Unit File**
   Create a new file in the `src/quiz/units` directory:

```
src/quiz/units/<category>_quiz_unit.py
```

2. **Implement the Unit Class**
   Define a new class named `<Category>QuizUnit` that inherits from `QuizUnitBase`.
   This class must implement all abstract methods defined in the base class:

* `transform_options_to_blueprint_unit`
* `transform_blueprint_unit_to_options`
* `generate_quiz`
* `parse_user_answer`
* `compare_answers`
* `prettify_answer`

3. **Register the Unit**
   Add your new unit to `QUIZ_UNIT_MAPPING` in `src/quiz/units/__init__.py`:

4. **Add Unit Tests**
   Create a test file at:

   ```
   src/quiz/tests/<category>_quiz_unit_test.py
   ```

   Write unit tests covering your new quiz unit’s behavior.

5. **Add Integration Test**
   Update `quiz_integration_test.py` to include integration coverage for your unit.

6. **Update Mapping Docstring**
   Edit `src/quiz/__init__.py` and update the docstring describing `QUIZ_UNIT_MAPPING` to mention your new unit and its category.

7. **Update Help Documentation**
   Append information about your new unit to `static/help.md`, including usage examples and option descriptions.
