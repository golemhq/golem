
class lazy_property(object):
    '''
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    '''

    def __init__(self,fget):
        self.fget = fget
        self.func_name = fget.__name__


    def __get__(self,obj,cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj,self.func_name,value)
        return value


class Dashboard(object):

    def __init__(self, driver):
        self.driver = driver

    @lazy_property
    def new_dropdown(self):
        new_dropdown = self.driver.find_element_by_id("newWI")
        return new_dropdown

    @lazy_property
    def create_story_menu_option(self):
        create_story_menu_option = self.driver.find_element_by_id("create-story")
        return create_story_menu_option

    @lazy_property
    def current_project_radio(self):
        current_project_radio = self.driver.find_element_by_id("project2")
        return current_project_radio

    @lazy_property
    def story_name(self):
        story_name_textfield = self.driver.find_element_by_id("storyName")
        return story_name_textfield

    @lazy_property
    def story_description(self):
        story_description_textfield = self.driver.find_element_by_id("storyDescription")
        return story_description_textfield

    @lazy_property
    def story_assignee(self):
        story_assignee_textfield = self.driver.find_element_by_id("assignee")
        return story_assignee_textfield

    @lazy_property
    def story_saveclose_button(self):
        story_saveclose_button = self.driver.find_element_by_xpath("//span[contains(text(), 'Save & Close')]")
        return story_saveclose_button




    
