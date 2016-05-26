"""
End-to-end tests for the simulator configuration. Sets up a server with
the backend, sends some basic queries to that server and verifies results
are as expected.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import logging
import random
import ga4gh.datamodel.reads as reads
import ga4gh.datamodel.references as references
import ga4gh.datamodel.variants as variants
import ga4gh.datamodel.sequenceAnnotations as features
import ga4gh.frontend as frontend
import ga4gh.protocol as protocol


class TestSimulatedStack(unittest.TestCase):
    """
    Tests the full stack for the Simulated backend by using the Flask
    testing client.
    """
    @classmethod
    def setUpClass(cls):
        # silence usually unhelpful CORS log
        logging.getLogger('ga4gh.frontend.cors').setLevel(logging.CRITICAL)
        # Set the random seed to make tests reproducible.
        random.seed(1)
        config = {
            "DATA_SOURCE": "simulated://",
            "SIMULATED_BACKEND_RANDOM_SEED": 1111,
            "SIMULATED_BACKEND_NUM_CALLS": 5,
            "SIMULATED_BACKEND_VARIANT_DENSITY": 1.0,
            "SIMULATED_BACKEND_NUM_VARIANT_SETS": 4,
            "SIMULATED_BACKEND_NUM_REFERENCE_SETS": 3,
            "SIMULATED_BACKEND_NUM_REFERENCES_PER_REFERENCE_SET": 4,
            "SIMULATED_BACKEND_NUM_ALIGNMENTS_PER_READ_GROUP": 5,
            # "DEBUG": True
        }
        frontend.reset()
        frontend.configure(
            baseConfig="TestConfig", extraConfig=config)
        cls.app = frontend.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.app = None

    def setUp(self):
        self.backend = frontend.app.backend
        self.dataRepo = self.backend.getDataRepository()
        self.dataset = self.dataRepo.getDatasets()[0]
        self.readGroupSet = self.dataset.getReadGroupSets()[0]
        self.readGroup = self.readGroupSet.getReadGroups()[0]
        self.reference = \
            self.readGroupSet.getReferenceSet().getReferences()[0]
        self.variantSet = self.dataset.getVariantSets()[0]
        self.variantAnnotationSet = \
            self.variantSet.getVariantAnnotationSets()[0]
        self.backend.setMaxResponseLength(10000)

    def getBadIds(self):
        """
        Returns a list of IDs that should not exist in the server and should
        raise a 404 error.
        """
        return ["1234:", "x"*100, ":", ":xx", "::", ":::", "::::"]

    def sendJsonPostRequest(self, path, data):
        """
        Sends a JSON request to the specified path with the specified data
        and returns the response.
        """
        return self.app.post(
            path, headers={'Content-type': 'application/json'},
            data=data)

    def sendSearchRequest(self, path, request, responseClass):
        """
        Sends the specified protocol request instance as JSON, and
        parses the result into an instance of the specified response.
        """
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        self.assertEqual(200, response.status_code)
        responseData = protocol.fromJson(response.data, responseClass)
        self.assertTrue(
            protocol.validate(
                protocol.toJson(responseData),
                type(responseData)))
        return responseData

    def sendObjectGetRequest(self, path, id_):
        """
        Sends a GET request to the specified path for an object with the
        specified ID and returns the response.
        """
        return self.app.get("{}/{}".format(path, id_))

    def sendGetObject(self, path, id_, responseClass):
        """
        Sends a get request and parses the value into an instance of the
        specified class.
        """
        response = self.sendObjectGetRequest(path, id_)
        self.assertEqual(200, response.status_code)
        obj = protocol.fromJson(response.data, responseClass)
        self.assertIsInstance(obj, responseClass)
        return obj

    def sendListReferenceBasesRequest(self, id_, request):
        """
        Sends a ListReferenceBasesRequest and parses the result into a
        ListReferenceBasesResponse.
        """
        path = '/references/{}/bases'.format(id_)
        response = self.app.get(
            path, query_string=protocol.toJsonDict(request))
        self.assertEqual(response.status_code, 200)
        obj = protocol.fromJson(
            response.data, protocol.ListReferenceBasesResponse)
        self.assertIsInstance(obj, protocol.ListReferenceBasesResponse)
        return obj

    def verifyVariantSetsEqual(self, gaVariantSet, variantSet):
        dataset = variantSet.getParentContainer()
        self.assertEqual(gaVariantSet.id, variantSet.getId())
        self.assertEqual(gaVariantSet.dataset_id, dataset.getId())
        self.assertEqual(gaVariantSet.name, variantSet.getLocalId())
        # TODO verify the metadata and other attributes.

    def verifyCallSetsEqual(self, gaCallSet, callSet):
        variantSet = callSet.getParentContainer()
        self.assertEqual(gaCallSet.id, callSet.getId())
        self.assertEqual(gaCallSet.name, callSet.getLocalId())
        self.assertEqual(gaCallSet.variant_set_ids, [variantSet.getId()])
        # TODO add some simulated info and check

    def verifyReadGroupSetsEqual(self, gaReadGroupSet, readGroupSet):
        dataset = readGroupSet.getParentContainer()
        self.assertEqual(gaReadGroupSet.id, readGroupSet.getId())
        self.assertEqual(gaReadGroupSet.dataset_id, dataset.getId())
        self.assertEqual(gaReadGroupSet.name, readGroupSet.getLocalId())
        self.assertEqual(
            len(gaReadGroupSet.read_groups), len(readGroupSet.getReadGroups()))
        for gaReadGroup, readGroup in zip(
                gaReadGroupSet.read_groups, readGroupSet.getReadGroups()):
            self.verifyReadGroupsEqual(gaReadGroup, readGroup)

    def verifyReadGroupsEqual(self, gaReadGroup, readGroup):
        self.assertEqual(gaReadGroup.id, readGroup.getId())

    def verifyDatasetsEqual(self, gaDataset, dataset):
        self.assertEqual(gaDataset.id, dataset.getId())
        self.assertEqual(gaDataset.name, dataset.getLocalId())
        self.assertEqual(gaDataset.description, dataset.getDescription())

    def verifyReferenceSetsEqual(self, gaReferenceSet, referenceSet):
        self.assertEqual(gaReferenceSet.id, referenceSet.getId())
        self.assertEqual(
            gaReferenceSet.md5checksum, referenceSet.getMd5Checksum())
        self.assertEqual(
            gaReferenceSet.ncbi_taxon_id, referenceSet.getNcbiTaxonId())
        self.assertEqual(
            gaReferenceSet.assembly_id, referenceSet.getAssemblyId())
        self.assertEqual(
            gaReferenceSet.source_uri, referenceSet.getSourceUri())
        self.assertEqual(
            gaReferenceSet.source_accessions,
            referenceSet.getSourceAccessions())
        self.assertEqual(
            gaReferenceSet.is_derived, referenceSet.getIsDerived())
        self.assertEqual(
            gaReferenceSet.name, referenceSet.getLocalId())

    def verifyFeatureSetsEqual(self, gaFeatureSet, featureSet):
        dataset = featureSet.getParentContainer()
        self.assertEqual(gaFeatureSet.id, featureSet.getId())
        self.assertEqual(gaFeatureSet.dataset_id, dataset.getId())
        self.assertEqual(gaFeatureSet.name, featureSet.getLocalId())

    def verifyFeaturesEquivalent(self, f1, f2):
        # at least modulo featureId. They can obviously have different
        # start/end/etc parameters if randomly generated from search vs get.
        self.assertEqual(f1.id, f2.id)
        self.assertEqual(f1.parent_id, f2.parent_id)
        self.assertEqual(f1.feature_set_id, f2.feature_set_id)

    def verifyReferencesEqual(self, gaReference, reference):
        self.assertEqual(gaReference.id, reference.getId())
        self.assertEqual(gaReference.name, reference.getName())
        self.assertEqual(gaReference.length, reference.getLength())
        self.assertEqual(gaReference.md5checksum, reference.getMd5Checksum())
        self.assertEqual(gaReference.ncbi_taxon_id, reference.getNcbiTaxonId())
        self.assertEqual(gaReference.source_uri, reference.getSourceUri())
        self.assertEqual(
            gaReference.source_accessions, reference.getSourceAccessions())
        self.assertEqual(gaReference.is_derived, reference.getIsDerived())
        self.assertEqual(
            gaReference.source_divergence, reference.getSourceDivergence())

    def verifySearchMethod(
            self, request, path, responseClass, objects, objectVerifier):
        """
        Verifies that the specified search request operates correctly
        and returns all the speficied objects. The specified verifier
        function checks that all the returned objects are equivalent
        to their datamodel counterparts.
        """
        request.page_size = len(objects)
        self.assertGreater(request.page_size, 0)
        responseData = self.sendSearchRequest(path, request, responseClass)
        self.assertEqual(responseData.next_page_token, "")
        responseList = getattr(
            responseData, protocol.getValueListName(responseClass))
        self.assertEqual(len(objects), len(responseList))
        for gaObject, datamodelObject in zip(responseList, objects):
            objectVerifier(gaObject, datamodelObject)

    def verifySearchResultsEmpty(self, request, path, responseClass):
        """
        Verifies that we get a successful response with an empty list of
        results.
        """
        responseData = self.sendSearchRequest(path, request, responseClass)
        self.assertEqual("", responseData.next_page_token)
        responseList = getattr(
            responseData, protocol.getValueListName(responseClass))
        self.assertEqual(0, len(responseList))

    def assertObjectNotFound(self, response):
        """
        Checks that the specified response contains a search failure.
        """
        self.assertEqual(404, response.status_code)
        error = protocol.fromJson(response.data, protocol.GAException)
        self.assertTrue(protocol.validate(protocol.toJson(error), type(error)))
        self.assertGreater(error.error_code, 0)
        self.assertGreater(len(error.message), 0)

    def assertObjectNotSupported(self, response):
        """
        Checks that the specified response returns a not supported 501 status
        """
        self.assertEqual(501, response.status_code)
        error = protocol.fromJson(response.data, protocol.GAException)
        self.assertTrue(protocol.validate(protocol.toJson(error), type(error)))
        self.assertGreater(error.error_code, 0)
        self.assertGreater(len(error.message), 0)

    def verifySearchMethodFails(self, request, path):
        """
        Verify that the specified search request fails with a 404.
        """
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        self.assertObjectNotFound(response)

    def verifySearchMethodNotSupported(self, request, path):
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        self.assertObjectNotSupported(response)

    def verifyGetMethodFails(self, path, id_):
        """
        Verifies the specified GET request failes with a 404.
        """
        response = self.sendObjectGetRequest(path, id_)
        self.assertObjectNotFound(response)

    def testGetDataset(self):
        path = "/datasets"
        for dataset in self.dataRepo.getDatasets():
            responseObject = self.sendGetObject(
                path, dataset.getId(), protocol.Dataset)
            self.verifyDatasetsEqual(responseObject, dataset)
        for badId in self.getBadIds():
            self.verifyGetMethodFails(path, badId)

    def testDatasetsSearch(self):
        request = protocol.SearchDatasetsRequest()
        datasets = self.dataRepo.getDatasets()
        path = '/datasets/search'
        self.verifySearchMethod(
            request, path, protocol.SearchDatasetsResponse, datasets,
            self.verifyDatasetsEqual)

    def testVariantSetsSearch(self):
        path = '/variantsets/search'
        for dataset in self.dataRepo.getDatasets():
            variantSets = dataset.getVariantSets()
            request = protocol.SearchVariantSetsRequest()
            request.dataset_id = dataset.getId()
            self.verifySearchMethod(
                request, path, protocol.SearchVariantSetsResponse, variantSets,
                self.verifyVariantSetsEqual)
        for badId in self.getBadIds():
            request = protocol.SearchVariantSetsRequest()
            request.dataset_id = badId
            self.verifySearchMethodFails(request, path)

    def testCallSetsSearch(self):
        path = '/callsets/search'
        for dataset in self.dataRepo.getDatasets():
            for variantSet in dataset.getVariantSets():
                callSets = variantSet.getCallSets()
                self.assertGreater(len(callSets), 0)
                request = protocol.SearchCallSetsRequest()
                request.variant_set_id = variantSet.getId()
                self.verifySearchMethod(
                    request, path, protocol.SearchCallSetsResponse, callSets,
                    self.verifyCallSetsEqual)
                # Check if we can search for the callset with a good name.
                for callSet in callSets:
                    request = protocol.SearchCallSetsRequest()
                    request.variant_set_id = variantSet.getId()
                    request.name = callSet.getLocalId()
                    self.verifySearchMethod(
                        request, path, protocol.SearchCallSetsResponse,
                        [callSet], self.verifyCallSetsEqual)
                # Check if we can search for the callset with a bad name.
                for badId in self.getBadIds():
                    request = protocol.SearchCallSetsRequest()
                    request.variant_set_id = variantSet.getId()
                    request.name = badId
                    self.verifySearchResultsEmpty(
                        request, path, protocol.SearchCallSetsResponse)
        # Check for searches within missing variantSets.
        for badId in self.getBadIds():
            request = protocol.SearchCallSetsRequest()
            request.variant_set_id = badId
            self.verifySearchMethodFails(request, path)

    def testReadGroupSetsSearch(self):
        path = '/readgroupsets/search'
        for dataset in self.dataRepo.getDatasets():
            readGroupSets = dataset.getReadGroupSets()
            request = protocol.SearchReadGroupSetsRequest()
            request.dataset_id = dataset.getId()
            self.verifySearchMethod(
                request, path, protocol.SearchReadGroupSetsResponse,
                readGroupSets, self.verifyReadGroupSetsEqual)
            # Check if we can search for the readGroupSet with a good name.
            for readGroupSet in readGroupSets:
                request = protocol.SearchReadGroupSetsRequest()
                request.dataset_id = dataset.getId()
                request.name = readGroupSet.getLocalId()
                self.verifySearchMethod(
                    request, path, protocol.SearchReadGroupSetsResponse,
                    [readGroupSet], self.verifyReadGroupSetsEqual)
            # Check if we can search for the readGroupSet with a bad name.
            for badId in self.getBadIds():
                request = protocol.SearchReadGroupSetsRequest()
                request.dataset_id = dataset.getId()
                request.name = badId
                self.verifySearchResultsEmpty(
                    request, path, protocol.SearchReadGroupSetsResponse)
        for badId in self.getBadIds():
            request = protocol.SearchReadGroupSetsRequest()
            request.dataset_id = badId
            self.verifySearchMethodFails(request, path)

    def testReferenceSetsSearch(self):
        request = protocol.SearchReferenceSetsRequest()
        referenceSets = self.dataRepo.getReferenceSets()
        path = '/referencesets/search'
        self.verifySearchMethod(
            request, path, protocol.SearchReferenceSetsResponse, referenceSets,
            self.verifyReferenceSetsEqual)

    def testReferencesSearch(self):
        path = '/references/search'
        for referenceSet in self.dataRepo.getReferenceSets():
            references = referenceSet.getReferences()
            request = protocol.SearchReferencesRequest()
            request.reference_set_id = referenceSet.getId()
            self.verifySearchMethod(
                request, path, protocol.SearchReferencesResponse, references,
                self.verifyReferencesEqual)
        for badId in self.getBadIds():
            request = protocol.SearchReferencesRequest()
            request.reference_set_id = badId
            self.verifySearchMethodFails(request, path)

    def verifyReferenceSearchFilters(
            self, objectList, hasAssemblyId, path, requestFactory,
            responseClass, objectVerifier):
        """
        Verifies the filtering functionality for the specified list of
        reference-like objects.
        """
        self.assertGreater(len(objectList), 2)
        for obj in objectList[1:]:
            request = requestFactory()
            # First, check the simple cases; 1 filter set, others null.
            request.md5checksum = obj.getMd5Checksum()
            self.verifySearchMethod(
                request, path, responseClass, [obj], objectVerifier)
            request.md5checksum = ""
            request.accession = obj.getSourceAccessions()[0]
            self.verifySearchMethod(
                request, path, responseClass, [obj], objectVerifier)
            request.accession = ""
            if hasAssemblyId:
                request.assembly_id = obj.getAssemblyId()
                self.verifySearchMethod(
                    request, path, responseClass, [obj], objectVerifier)
                request.assembly_id = ""
            # Now check one good value and some bad values.
            request.md5checksum = obj.getMd5Checksum()
            badAccessions = [
                "no such accession", objectList[0].getSourceAccessions()[0]]
            for accession in badAccessions:
                request.accession = accession
                self.verifySearchResultsEmpty(request, path, responseClass)
            request.accession = ""
            if hasAssemblyId:
                badAssemblyIds = [
                    "no such asssembly", objectList[0].getAssemblyId()]
                for assemblyId in badAssemblyIds:
                    request.assembly_id = assemblyId
                    self.verifySearchResultsEmpty(request, path, responseClass)
                request.assembly_id = ""

    def testReferencesSearchFilters(self):
        path = '/references/search'
        for referenceSet in self.dataRepo.getReferenceSets():

            def requestFactory():
                request = protocol.SearchReferencesRequest()
                request.reference_set_id = referenceSet.getId()
                return request
            self.verifyReferenceSearchFilters(
                referenceSet.getReferences(), False, path, requestFactory,
                protocol.SearchReferencesResponse, self.verifyReferencesEqual)

    def testReferenceSetsSearchFilters(self):
        path = '/referencesets/search'

        def requestFactory():
            return protocol.SearchReferenceSetsRequest()
        self.verifyReferenceSearchFilters(
            self.dataRepo.getReferenceSets(), True, path, requestFactory,
            protocol.SearchReferenceSetsResponse,
            self.verifyReferenceSetsEqual)

    def testGetVariantSet(self):
        path = "/variantsets"
        for dataset in self.dataRepo.getDatasets():
            for variantSet in dataset.getVariantSets():
                responseObject = self.sendGetObject(
                    path, variantSet.getId(), protocol.VariantSet)
                self.verifyVariantSetsEqual(responseObject, variantSet)
            for badId in self.getBadIds():
                variantSet = variants.AbstractVariantSet(dataset, badId)
                self.verifyGetMethodFails(path, variantSet.getId())
        for badId in self.getBadIds():
            self.verifyGetMethodFails(path, badId)

    def testGetVariantAnnotationSet(self):
        path = "/variantannotationsets"
        for dataset in self.dataRepo.getDatasets():
            for variantSet in dataset.getVariantSets():
                for vas in variantSet.getVariantAnnotationSets():
                    responseObject = self.sendGetObject(
                        path, vas.getId(), protocol.VariantAnnotationSet)
                    self.assertEqual(
                        vas.getId(), responseObject.id,
                        "The requested ID should match the returned")
        for badId in self.getBadIds():
            self.verifyGetMethodFails(path, badId)

    def testGetVariant(self):
        # get a variant from the search method
        referenceName = '1'
        start = 0
        request = protocol.SearchVariantsRequest()
        request.variant_set_id = self.variantSet.getId()
        request.reference_name = referenceName
        request.start = start
        request.end = 2**16
        path = '/variants/search'
        responseData = self.sendSearchRequest(
            path, request, protocol.SearchVariantsResponse)
        variants = responseData.variants[:10]

        # get 'the same' variant using the get method
        for variant in variants:
            path = '/variants'
            responseObject = self.sendGetObject(
                path, variant.id, protocol.Variant)
            self.assertEqual(responseObject, variant)

    def testGetReferenceSet(self):
        path = "/referencesets"
        for referenceSet in self.dataRepo.getReferenceSets():
            responseObject = self.sendGetObject(
                path, referenceSet.getId(), protocol.ReferenceSet)
            self.verifyReferenceSetsEqual(responseObject, referenceSet)
        for badId in self.getBadIds():
            self.verifyGetMethodFails(path, badId)

    def testGetReference(self):
        path = "/references"
        for referenceSet in self.dataRepo.getReferenceSets():
            for reference in referenceSet.getReferences():
                responseObject = self.sendGetObject(
                    path, reference.getId(), protocol.Reference)
                self.verifyReferencesEqual(responseObject, reference)
            for badId in self.getBadIds():
                referenceSet = references.AbstractReferenceSet(badId)
                self.verifyGetMethodFails(path, referenceSet.getId())
        for badId in self.getBadIds():
            self.verifyGetMethodFails(path, badId)

    def testGetCallSet(self):
        path = "/callsets"
        for dataset in self.dataRepo.getDatasets():
            for variantSet in dataset.getVariantSets():
                for callSet in variantSet.getCallSets():
                    responseObject = self.sendGetObject(
                        path, callSet.getId(), protocol.CallSet)
                    self.verifyCallSetsEqual(responseObject, callSet)
                for badId in self.getBadIds():
                    callSet = variants.CallSet(variantSet, badId)
                    self.verifyGetMethodFails(path, callSet.getId())
        for badId in self.getBadIds():
            self.verifyGetMethodFails(path, badId)

    def testGetReadGroup(self):
        path = "/readgroups"
        for dataset in self.dataRepo.getDatasets():
            for readGroupSet in dataset.getReadGroupSets():
                for readGroup in readGroupSet.getReadGroups():
                    responseObject = self.sendGetObject(
                        path, readGroup.getId(), protocol.ReadGroup)
                    self.verifyReadGroupsEqual(responseObject, readGroup)
                for badId in self.getBadIds():
                    readGroup = reads.AbstractReadGroup(readGroupSet, badId)
                    self.verifyGetMethodFails(path, readGroup.getId())
            for badId in self.getBadIds():
                readGroupSet = reads.AbstractReadGroupSet(dataset, badId)
                self.verifyGetMethodFails(path, readGroupSet.getId())
        for badId in self.getBadIds():
            self.verifyGetMethodFails(path, badId)

    def testVariantsSearch(self):
        referenceName = '1'

        request = protocol.SearchVariantsRequest()
        request.reference_name = referenceName
        request.start = 0
        request.end = 0
        request.variant_set_id = self.variantSet.getId()

        # Request windows is too small, no results
        path = '/variants/search'
        responseData = self.sendSearchRequest(
            path, request, protocol.SearchVariantsResponse)
        self.assertEqual("", responseData.next_page_token)
        self.assertEqual(0, len(responseData.variants))

        # Larger request window, expect results
        request.end = 2 ** 16
        responseData = self.sendSearchRequest(
            path, request, protocol.SearchVariantsResponse)
        self.assertTrue(protocol.validate(
            protocol.toJson(responseData), protocol.SearchVariantsResponse))
        self.assertGreater(len(responseData.variants), 0)

        # Verify all results are in the correct range, set and reference
        for variant in responseData.variants:
            self.assertGreaterEqual(variant.start, 0)
            self.assertLessEqual(variant.end, 2 ** 16)
            self.assertEqual(variant.variant_set_id, self.variantSet.getId())
            self.assertEqual(variant.reference_name, referenceName)

        # TODO: Add more useful test scenarios, including some covering
        # pagination behavior.

    def testVariantAnnotationSetsSearch(self):
        self.assertIsNotNone(self.variantAnnotationSet)

        request = protocol.SearchVariantAnnotationSetsRequest()

        request.variant_set_id = "b4d=="
        path = '/variantannotationsets/search'
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.GAException)
        self.assertTrue(protocol.validate(protocol.toJson(responseData),
                                          protocol.GAException))
        self.assertEqual(responseData.error_code, 758389611)
        self.assertEqual(responseData.message,
                         'No object of this type exists with id \'b4d==\'')

        request.variant_set_id = self.variantSet.getId()
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.
                                         SearchVariantAnnotationSetsResponse)
        self.assertTrue(protocol.validate(
            protocol.toJson(responseData),
            protocol.SearchVariantAnnotationSetsResponse))
        self.assertGreater(len(responseData.variant_annotation_sets), 0,
                           "Expect some results for a known good ID")
        # TODO check the instance variables; we should be able to match
        # the values from the protocol object we get back with the values
        # in the original variantAnnotationSet.

    def testVariantAnnotationsSearch(self):
        self.assertIsNotNone(self.variantAnnotationSet)

        request = protocol.SearchVariantAnnotationsRequest()
        # TODO split these into separate tests, and factor out the duplicated
        # code.

        path = '/variantannotations/search'
        request.start = 0
        request.end = 1000000
        request.page_size = 1
        request.reference_name = "1"
        request.variant_annotation_set_id = self.variantAnnotationSet.getId()
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.
                                         SearchVariantAnnotationsResponse)
        self.assertGreater(len(responseData.variant_annotations), 0)
        self.assertIsNotNone(
            responseData.next_page_token,
            "Expected more than one page of results")

        request = protocol.SearchVariantAnnotationsRequest()
        request.variant_annotation_set_id = self.variantAnnotationSet.getId()
        request.start = 0
        request.end = 10
        request.reference_name = "1"

        request.effects.add().id = "ThisIsNotAnEffect"

        # request.effects.extend([{"id": "ThisIsNotAnEffect"}])
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.
                                         SearchVariantAnnotationsResponse)
        self.assertEquals(
            len(responseData.variant_annotations), 0,
            "There should be no results for a nonsense effect")

        request = protocol.SearchVariantAnnotationsRequest()
        request.variant_annotation_set_id = self.variantAnnotationSet.getId()
        request.start = 0
        request.end = 10
        request.reference_name = "1"
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.
                                         SearchVariantAnnotationsResponse)
        self.assertGreater(len(responseData.variant_annotations), 0)
        for ann in responseData.variant_annotations:
            self.assertGreater(
                len(ann.transcript_effects), 0,
                ("When no effects are requested ensure "
                    "some transcript effects are still present"))

        request = protocol.SearchVariantAnnotationsRequest()
        request.variant_annotation_set_id = self.variantAnnotationSet.getId()
        request.start = 0
        request.end = 5
        request.reference_name = "1"
        request.effects.add().id = "SO:0001627"
        request.effects.add().id = "B4DID"
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.
                                         SearchVariantAnnotationsResponse)
        responseLength = len(responseData.variant_annotations)
        self.assertGreater(
            responseLength, 0,
            "There should be some results for a known effect")
        for ann in responseData.variant_annotations:
            effectPresent = False
            for effect in ann.transcript_effects:
                for featureType in effect.effects:
                    if featureType.id in map(
                            lambda e: e.id, request.effects):
                        effectPresent = True
            self.assertEquals(
                True, effectPresent,
                "The ontology term should appear at least once")

        request = protocol.SearchVariantAnnotationsRequest()
        request.variant_annotation_set_id = self.variantAnnotationSet.getId()
        request.start = 0
        request.end = 5
        request.reference_name = "1"
        request.effects.add().id = "B4DID"
        request.effects.add().id = "SO:0001627"
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.
                                         SearchVariantAnnotationsResponse)
        self.assertEqual(
            len(responseData.variant_annotations),
            responseLength,
            "Order shall not affect results")
        for ann in responseData.variant_annotations:
            effectPresent = False
            for effect in ann.transcript_effects:
                for featureType in effect.effects:
                    if featureType.id in map(
                            lambda e: e.id, request.effects):
                        effectPresent = True
            self.assertEquals(
                True,
                effectPresent,
                "The ontology term should appear at least once")

        request = protocol.SearchVariantAnnotationsRequest()
        request.variant_annotation_set_id = self.variantAnnotationSet.getId()
        request.start = 0
        request.end = 5
        request.reference_name = "1"
        request.effects.add().id = "SO:0001627"
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.
                                         SearchVariantAnnotationsResponse)
        self.assertGreater(len(responseData.variant_annotations), 0,
                           "There should be some results for a good effect ID")
        for ann in responseData.variant_annotations:
            effectPresent = False
            for effect in ann.transcript_effects:
                for featureType in effect.effects:
                    if featureType.id in map(
                            lambda e: e.id, request.effects):
                        effectPresent = True
            self.assertEquals(True, effectPresent,
                              "The ontology term should appear at least once")

        request = protocol.SearchVariantAnnotationsRequest()
        request.variant_annotation_set_id = self.variantAnnotationSet.getId()
        request.start = 0
        request.end = 10
        request.reference_name = "1"
        request.effects.add().id = "SO:0001627"
        request.effects.add().id = "SO:0001791"
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        responseData = protocol.fromJson(response.data, protocol.
                                         SearchVariantAnnotationsResponse)
        self.assertGreater(len(responseData.variant_annotations), 0)

    def testGetFeatureSet(self):
        path = "/featuresets"
        for dataset in self.dataRepo.getDatasets():
            for featureSet in dataset.getFeatureSets():
                responseObject = self.sendGetObject(
                    path, featureSet.getId(), protocol.FeatureSet)
                self.verifyFeatureSetsEqual(responseObject, featureSet)
            for badId in self.getBadIds():
                featureSet = features.AbstractFeatureSet(dataset, badId)
                self.verifyGetMethodFails(path, featureSet.getId())
        for badId in self.getBadIds():
            self.verifyGetMethodFails(path, badId)

    def testFeatureSetsSearch(self):
        path = '/featuresets/search'
        for dataset in self.dataRepo.getDatasets():
            featureSets = dataset.getFeatureSets()
            request = protocol.SearchFeatureSetsRequest()
            request.dataset_id = dataset.getId()
            self.verifySearchMethod(
                request, path, protocol.SearchFeatureSetsResponse, featureSets,
                self.verifyFeatureSetsEqual)
        for badId in self.getBadIds():
            request = protocol.SearchFeatureSetsRequest()
            request.dataset_id = badId
            self.verifySearchMethodFails(request, path)

    def testGetFeature(self):
        dataset = self.dataRepo.getDatasets()[0]
        featureSet = dataset.getFeatureSets()[0]
        request = protocol.SearchFeaturesRequest()
        request.feature_set_id = featureSet.getId()
        request.reference_name = "chr1"
        request.start = 0
        request.end = 2**16
        path = '/features/search'
        responseData = self.sendSearchRequest(
            path, request, protocol.SearchFeaturesResponse)
        features = responseData.features[:10]

        # get 'the same' feature using the get method
        for feature in features:
            path = '/features'
            responseObject = self.sendGetObject(
                path, feature.id, protocol.Feature)
            self.verifyFeaturesEquivalent(responseObject, feature)

    def testFeaturesSearch(self):
        dataset = self.dataRepo.getDatasets()[0]
        featureSet = dataset.getFeatureSets()[0]
        referenceName = 'chr1'

        request = protocol.SearchFeaturesRequest()
        request.reference_name = referenceName
        request.feature_set_id = featureSet.getId()

        # Request window is outside of simulated dataset bounds, no results
        request.start = 0
        request.end = 1
        request.parent_id = ''
        path = '/features/search'
        responseData = self.sendSearchRequest(
            path, request, protocol.SearchFeaturesResponse)
        self.assertEqual('', responseData.next_page_token)
        self.assertEqual(0, len(responseData.features))

        # Larger request window, expect results
        request.start = 0
        request.end = 2 ** 16
        responseData = self.sendSearchRequest(
            path, request, protocol.SearchFeaturesResponse)

        self.assertGreater(len(responseData.features), 0)

        # Verify all results are in the correct range, set and reference
        for feature in responseData.features:
            self.assertGreaterEqual(feature.start, 0)
            self.assertLessEqual(feature.end, 2 ** 16)
            self.assertEqual(feature.feature_set_id, featureSet.getId())
            self.assertEqual(feature.reference_name, referenceName)

    def testListReferenceBases(self):
        for referenceSet in self.dataRepo.getReferenceSets():
            for reference in referenceSet.getReferences():
                id_ = reference.getId()
                length = reference.getLength()
                sequence = reference.getBases(0, length)
                # fetch the bases
                args = protocol.ListReferenceBasesRequest()
                response = self.sendListReferenceBasesRequest(id_, args)
                self.assertEqual(response.sequence, sequence)
                # Try some simple slices.
                ranges = [(0, length), (0, 1), (length - 1, length)]
                for start, end in ranges:
                    args = protocol.ListReferenceBasesRequest()
                    args.start, args.end = start, end
                    response = self.sendListReferenceBasesRequest(id_, args)
                    self.assertEqual(response.sequence, sequence[start:end])
                    self.assertEqual("", response.next_page_token)
                    self.assertEqual(response.offset, start)

    def testListReferenceBasesErrors(self):
        referenceSet = self.dataRepo.getReferenceSets()[0]
        for badId in self.getBadIds():
            path = '/references/{}/bases'.format(badId)
            response = self.app.get(path)
            self.assertEqual(response.status_code, 404)
            reference = references.AbstractReference(referenceSet, badId)
            path = '/references/{}/bases'.format(reference.getId())
            response = self.app.get(path)
            self.assertEqual(response.status_code, 404)
        path = '/references/{}/bases'.format(self.reference.getId())
        length = self.reference.getLength()
        badRanges = [(-1, 0), (-1, -1), (length, 0), (0, length + 1)]
        for start, end in badRanges:
            args = protocol.ListReferenceBasesRequest()
            args.start, args.end = start, end
            response = self.app.get(
                path, query_string=protocol.toJsonDict(args))
            self.assertEqual(response.status_code, 416)

    def testListReferenceBasesPaging(self):
        id_ = self.reference.getId()
        length = self.reference.getLength()
        completeSequence = self.reference.getBases(0, length)
        for start, end in [(0, length), (5, 10), (length // 2, length)]:
            sequence = completeSequence[start: end]
            for pageSize in [1, 2, length - 1]:
                self.backend.setMaxResponseLength(pageSize)
                args = protocol.ListReferenceBasesRequest()
                args.start, args.end = start, end
                response = self.sendListReferenceBasesRequest(id_, args)
                self.assertEqual(response.sequence, sequence[:pageSize])
                self.assertEqual(response.offset, start)
                sequenceFragments = [response.sequence]
                while response.next_page_token is not "":
                    args = protocol.ListReferenceBasesRequest()
                    args.page_token = response.next_page_token
                    args.start, args.end = start, end
                    response = self.sendListReferenceBasesRequest(id_, args)
                    self.assertGreater(len(response.sequence), 0)
                    sequenceFragments.append(response.sequence)
                    offset = response.offset
                    self.assertEqual(
                        response.sequence,
                        completeSequence[
                            offset: offset + len(response.sequence)])

                self.assertEqual("".join(sequenceFragments), sequence)

    def testReads(self):
        path = '/reads/search'
        for dataset in self.dataRepo.getDatasets():
            for readGroupSet in dataset.getReadGroupSets():
                referenceSet = readGroupSet.getReferenceSet()
                for reference in referenceSet.getReferences():
                    for readGroup in readGroupSet.getReadGroups():
                        # search reads
                        request = protocol.SearchReadsRequest()
                        request.read_group_ids.append(readGroup.getId())
                        request.reference_id = reference.getId()
                        responseData = self.sendSearchRequest(
                            path, request, protocol.SearchReadsResponse)
                        alignments = responseData.alignments
                        self.assertGreater(len(alignments), 0)
                        for alignment in alignments:
                            # TODO more tests here: this is very weak.
                            self.assertEqual(
                                alignment.read_group_id, readGroup.getId())

    def testUnsupportedReadOperations(self):
        path = '/reads/search'

        # unmapped Reads
        request = protocol.SearchReadsRequest()
        request.read_group_ids.extend([self.readGroup.getId()])
        request.reference_id = ""
        self.verifySearchMethodNotSupported(request, path)

        # multiple ReadGroupSets set mismatch
        request.read_group_ids.append(self.readGroup.getId())
        request.read_group_ids.append("42")
        request.reference_id = self.reference.getId()
        response = self.sendJsonPostRequest(path, protocol.toJson(request))
        self.assertEqual(400, response.status_code)

    def testReadsMultipleReadGroupSets(self):
        path = '/reads/search'
        readGroupIds = [
            readGroup.getId() for readGroup in
            self.readGroupSet.getReadGroups()]
        referenceId = self.reference.getId()

        request = protocol.SearchReadsRequest()
        request.read_group_ids.extend(readGroupIds)
        request.reference_id = referenceId
        responseData = self.sendSearchRequest(
            path, request, protocol.SearchReadsResponse)

        readGroupAlignments = []
        for readGroup in self.readGroupSet.getReadGroups():
            readGroupAlignments.extend(list(
                readGroup.getReadAlignments(referenceId, None, None)))

        alignments = responseData.alignments
        self.assertEqual(len(alignments), len(readGroupAlignments))
        for alignment, rgAlignment in zip(alignments, readGroupAlignments):
            self.assertEqual(alignment.id, rgAlignment.id)
            self.assertEqual(alignment.read_group_id,
                             rgAlignment.read_group_id)
