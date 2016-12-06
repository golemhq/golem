
import json
import os
import uuid


class TestCaseList:

    def __init__(self, project=None, list_name=None, is_execution=False):
        self.project = project
        self.list_name = list_name
        self.is_execution = is_execution
        self.path = os.path.join(
            'projects', self.project, 'testcases', '{0}.json'.format(self.list_name))
        return


    def save_changes(self, new_data):
        # verify first column is 'inner_id'
        if new_data[0][0] == 'inner_id':
            # if test case does not have inner_id
            # generate unique identifier
            for row in new_data[1:]:
                if not row[0]:
                    row[0] = str(uuid.uuid4());
        else:
            print("first column is not inner_id")
            
        with open(self.path, 'w') as test_case_file:    

            json.dump(new_data, test_case_file, indent=4)

        return


    def create_new(self, default_fields):

        with open(self.path, 'w+') as out_file:

            #inner_id is for internal use, not shown to user
            default_headers = ['inner_id'] + default_fields
            first_row = [''] * len(default_headers)
            initial_content = [
                default_headers,
                first_row
            ]
            json.dump(initial_content, out_file, indent=4)

        return


    def create_from_import(self, import_data):

        with open(self.path, 'w+') as out_file:

            import_data[0].insert(0, 'inner_id')
            for i in range(1, len(import_data)):
                import_data[i].insert(0, '')

            json.dump(import_data, out_file, indent=4)

        return


    def get_data(self):
        with open(self.path) as test_case_file:    
            test_case_data = json.load(test_case_file)
            return test_case_data


    def delete(self):
        result = {
            'errors': []
        }
        if not os.path.isfile(self.path):
            result['errors'].append(
                'There is no file with name {}'.format(self.list_name))

        if not result['errors']:
            os.remove(self.path)

        return result
