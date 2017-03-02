import operator
import os.path
import random
from pathlib import Path

from app.person import Fellow, Person, Staff
from app.room import LivingSpace, Office, Room


class Dojo(object):
    all_office = []
    all_living_space = []
    all_persons_in_dojo = {}
    unallocated_persons = {}

    @classmethod
    def create_room(cls, room_type, room_name):
        output = ""
        for name in room_name:
            combine_rooms = cls.all_office + cls.all_living_space
            if name in [room.room_name for room in combine_rooms]:
                output = output + ('Room already exist.\n')
            elif room_type == 'office':
                new_room = Office(name)
                cls.all_office.append(new_room)
                output = output + \
                    ('An office called %s has been created.\n' % name)
            elif room_type == 'living':
                new_room = LivingSpace(name)
                cls.all_living_space.append(new_room)
                output = output + \
                    ('A living space called %s has been created.\n' % name)
        return output

    @classmethod
    def add_person_input_check(cls, first_name, last_name, person_type, wants_accomodation='n'):
        if wants_accomodation == 'y' or wants_accomodation == 'n':
            if person_type == 'fellow':
                if first_name.isalpha() and last_name.isalpha():
                    cls.add_fellow(first_name, last_name,
                                   person_type, wants_accomodation)
                else:
                    return('First name and last name can only be alphabets.')
            elif person_type == 'staff':
                if first_name.isalpha() and last_name.isalpha():
                    cls.add_staff(first_name, last_name,
                                  person_type, wants_accomodation)
            else:
                return('A person can only be a fellow or a staff.')
        else:
            return("wants_accomodation can only be 'Y' or 'N'.")

    @classmethod
    def id_generator(cls, person_type):
        if person_type == 'staff':
            staff_id = 'DJ-S-' + str(random.randint(0x1000, 0x270F))
            while staff_id in cls.all_persons_in_dojo:
                staff_id = 'DJ-S-' + str(random.randint(0x1000, 0x270F))
            return(staff_id)
        else:
            fellow_id = 'DJ-F-' + str(random.randint(0x1000, 0x270F))
            while fellow_id in cls.all_persons_in_dojo:
                fellow_id = 'DJ-F-' + str(random.randint(0x1000, 0x270F))
            return(fellow_id)

    @classmethod
    def add_fellow(cls, first_name, last_name,
                   person_type, wants_accomodation='n'):
        new_person = Fellow(first_name, last_name)
        unique_id = cls.id_generator(person_type)
        if wants_accomodation == 'y':
            person_living = cls.get_available_room('living')
            person_office = cls.get_available_room('office')
            if person_living and person_office:
                cls.all_persons_in_dojo[unique_id] = new_person
                person_living.room_members[unique_id] = new_person
                person_office.room_members[unique_id] = new_person
                new_person.assigned_room[
                    'my_living'] = person_living
                new_person.assigned_room[
                    'my_office'] = person_office
                return(new_person.full_name + ' with I.D number '
                       + unique_id + ' has been allocated the '
                       + person_living.room_type + ' ' + person_living.room_name)
            elif person_office is None and person_living is None:
                cls.unallocated_persons[unique_id] = [
                    new_person.full_name, 'Living Space']
                cls.unallocated_persons[unique_id] = [
                    new_person.full_name, 'Office']
                return('No office and living room available.')
            elif person_office:
                cls.all_persons_in_dojo[unique_id] = new_person
                person_office.room_members[
                    unique_id] = new_person
                new_person.assigned_room[
                    'my_office'] = person_office
                cls.unallocated_persons[unique_id] = [
                    new_person.full_name, 'Living Space']
                return(new_person.full_name + ' with I.D number '
                       + unique_id + ' has been allocated the '
                       + person_office.room_type + ' ' + person_office.room_name
                       + '\n Only an Office was allocated. No available Living Space.')
            else:
                cls.all_persons_in_dojo[unique_id] = new_person
                person_living.room_members[
                    unique_id] = new_person
                new_person.assigned_room[
                    'my_living'] = person_living
                cls.unallocated_persons[unique_id] = [
                    new_person.full_name, 'Office']
                return(new_person.full_name + ' with I.D number '
                       + unique_id + ' has been allocated the '
                       + person_living.room_type + ' ' + person_living.room_name
                       + '\n Only a Living Space was allocated. No available Office.')
        else:
            person_office = cls.get_available_room('office')
            if person_office:
                cls.all_persons_in_dojo[unique_id] = new_person
                person_office.room_members[
                    unique_id] = new_person
                new_person.assigned_room[
                    'my_office'] = person_office
                return(new_person.full_name + ' with I.D number '
                       + unique_id + ' has been allocated the '
                       + person_office.room_type + ' ' + person_office.room_name)
            else:
                cls.unallocated_persons[
                    unique_id] = [new_person.full_name, 'Office']
                return('No Office available.')

    @classmethod
    def add_staff(cls, first_name, last_name, person_type, wants_accomodation='n'):
        new_person = Staff(first_name, last_name)
        unique_id = cls.id_generator(person_type)
        person_office = cls.get_available_room('office')
        if wants_accomodation == 'y' and person_office:
            cls.all_persons_in_dojo[unique_id] = new_person
            person_office.room_members[unique_id] = new_person
            output = '\nSorry. Only fellows can have a living space.'
            return(new_person.full_name + ' with I.D number '
                   + unique_id + ' has been allocated the '
                   + person_office.room_type + ' '
                   + person_office.room_name + output)
        elif person_office:
            cls.all_persons_in_dojo[unique_id] = new_person
            person_office.room_members[unique_id] = new_person
            new_person.assigned_room['my_office'] = person_office
            return(new_person.full_name + ' with I.D number '
                   + unique_id + ' has been allocated the '
                   + person_office.room_type + ' ' + person_office.room_name)
        else:
            cls.unallocated_persons[
                unique_id] = [new_person.full_name, 'Office']
            return('No office is available.')

    @classmethod
    def get_available_room(cls, room_type):
        """ Gets any available office at random"""
        available_room = []
        if room_type == 'office':
            for room in cls.all_office:
                if len(room.room_members) < 6:
                    available_room.append(room)
            if available_room:
                return(random.choice(available_room))
        else:
            for room in cls.all_living_space:
                if len(room.room_members) < 4:
                    available_room.append(room)
            if available_room:
                return(random.choice(available_room))

    @classmethod
    def print_room(cls, room_name):
        """ Gets any given room if created and
         prints out the occupants if any."""
        combine_rooms = cls.all_living_space + cls.all_office
        if any(x.room_name == room_name for x in combine_rooms):
            for room in combine_rooms:
                if room.room_name == room_name:
                    if not any(room.room_members):
                        return('There are no occupants in ' +
                               room.room_name + ' at the moment.')
                    else:
                        output = ''
                        for key in sorted(room.room_members.values(),
                                          key=operator.attrgetter('full_name')):
                            output += key.full_name + ' --> ' \
                                + key.person_type + '\n'
                        return (output)
        else:
            return('No room named', room_name, 'at the moment.')

    @classmethod
    def print_allocations(cls, filename=''):
        """ Gets a list """
        if '.txt' in filename:
            path = 'data/' + filename
        else:
            path = 'data/' + filename + '.txt'
        combine_rooms = cls.all_living_space + cls.all_office
        if filename:
            print('logging all allocated persons to ' + filename + '...')
            my_file = open(path, 'w')
            for room in combine_rooms:
                if len(room.room_members) > 0:
                    output = room.room_name.upper() + '\n'
                    output = output + ('-' * 30) + '\n'
                    output = output + \
                        (', '.join(
                            [obj.full_name for obj in room.room_members.values()]) + '\n')
                    my_file.write(output)
                    my_file.close()
                else:
                    return('There are no occupants in any room.')
        else:
            for room in combine_rooms:
                if len(room.room_members) > 0:
                    output = room.room_name.upper() + '\n'
                    output = output + ('-' * 30) + '\n'
                    output = output + \
                        (', '.join(
                            [obj.full_name for obj in room.room_members.values()]) + '\n')
                    return(output)
                else:
                    return('There are no occupants in any room.')

    @classmethod
    def print_unallocated(cls, filename=''):
        """ Gets a list """
        if '.txt' in filename:
            path = 'data/' + filename
        else:
            path = 'data/' + filename + '.txt'
        if filename:
            head = 'UNALLOCATED LIST\n'
            head = head + ('-' * 30) + '\n'
            if len(cls.unallocated_persons) > 0:
                print('logging all allocated persons to ' + path + '...')
                my_file = open(path, 'w')
                my_file.write(head)
                for value in sorted(cls.unallocated_persons.values()):
                    my_file.write(('{v1}: {v2}\n'.format(
                        v1=value[0], v2=value[1])))
                my_file.close()
            else:
                return('There are no unallocated persons.')
        else:
            head = 'UNALLOCATED LIST\n'
            head = head + ('-' * 30) + '\n'
            if len(cls.unallocated_persons) > 0:
                output = ''
                for value in sorted(cls.unallocated_persons.values()):
                    output = output + ('{v1}: {v2}\n'.format(
                        v1=value[0], v2=value[1]))
                return(head + output)
            else:
                return('There are no unallocated persons.')
