import os

from aimi.generic.Config import UnsortedInstance
from aimi.generic.modules.importer.DataImporter import DataImporter

class NrrdImporter(DataImporter):

    def task(self) -> None:

        # TODO: self.c['base_dir'] will be used here in the future but currrently is /app/data/sorted, whereas the actual instance base is "sorted" because "/app/data" is the data handler base path. Add a global rel/abs path resolving mechanism to handle these kinds safely. Also add this (and all actions) to a describing log file so everybody can see what's going on in terms of data handling!
        # NOTE: Thinking about this, I will put the current dynamic resolving folder structure approach under revision. Although it looks nice (and will make debugging / inspection a ton easyer), there is no neeed to have a well defined folder structure hidden in the docker if we keep track of all files anyways, especially since we always could export the files (as with the organizer module). However, the current approach however makes the pipeline more compatible with (our)traditional folder structure. Thinking about transparency, the jupyter notebooks might benefit from a well-defined folder structure! SO pro's and con's.

        #self.setBasePath('sorted') # --> no base path used for single file importer.

        # get input data
        instances = self.config.data.instances
        assert len(instances) == 1, "Error: too many instances. Sorter expxts a single instance."
        instance = instances[0]
        assert type(instance) == UnsortedInstance, "Error: instance must be unsorted."

        # input nrrd file name
        input_file_name = self.c['input_file_name']
        self.v("importing", input_file_name)

        #
        self.addNrrdCT(input_file_name)

        # let the data importer base module care for the rest!
        super().task()