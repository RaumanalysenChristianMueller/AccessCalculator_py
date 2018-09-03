# -*- coding: utf-8 -*-

import processing
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFolderDestination)


class multipleServiceAreas(QgsProcessingAlgorithm):
    
    """
    This script calculates multiple service areas
    """

    toPoints = 'toPoints'
    networkLines = 'networkLines'
    fromDist = 'fromDist'
    toDist = 'toDist'
    intervalDist = 'intervalDist'
    OUTPUT = 'output'
    

    def initAlgorithm(self, config = None):
        
        # define input parameters
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.toPoints,
                self.tr('Zu erreichende Punkte'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.networkLines,
                self.tr('Wegenetz'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.fromDist,
                self.tr('minimale Entfernung'),
                QgsProcessingParameterNumber.Integer, 0, False, 0, 100000
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.toDist,
                self.tr('maximale Entfernung'),
                QgsProcessingParameterNumber.Integer, 1000, False, 1, 100000
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.intervalDist,
                self.tr('Abstand zwischen den Entfernungsklassen'),
                QgsProcessingParameterNumber.Integer, 100, False, 1, 100000
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                self.tr('Ausgabe-Ordner')
            )
        )
        
        
    def processAlgorithm(self, parameters, context, feedback):
        
        # get inputs from QGIS
        toPoints = self.parameterAsVectorLayer(parameters, self.toPoints, context)
        networkLines = self.parameterAsVectorLayer(parameters, self.networkLines, context)
        fromDist = self.parameterAsInt(parameters, self.fromDist, context)
        toDist = self.parameterAsInt(parameters, self.toDist, context)
        intervalDist = self.parameterAsInt(parameters, self.intervalDist, context)
        outDir = self.parameterAsString(parameters, self.OUTPUT, context)
        
        # prepare output directory string
        outDir = outDir.replace('/', '\\')
        
        # get service area intervals
        valCuts = range(fromDist, toDist, intervalDist)
        
        # loop over each class break
        prbVal = 0
        for i in valCuts:
            
            # set progress bar
            feedback.setProgress(prbVal/len(valCuts) * 100)
            
            # get this output name
            this_output = 'ogr:dbname=\'' + outDir + '/multipleDienstbereiche.gpkg\' table=\"' + str(i) + 'm\" (geom) sql='
            
            # perform accessibility analysis
            temp_params = {
                'INPUT': networkLines,
                'START_POINTS': toPoints,
                'STRATEGY': 0,
                'TRAVEL_COST': i,
                'DIRECTION_FIELD': None,
                'VALUE_FORWARD':'',
                'VALUE_BACKWARD':'',
                'VALUE_BOTH':'',
                'DEFAULT_DIRECTION':2,
                'SPEED_FIELD':None,
                'DEFAULT_SPEED':5,
                'TOLERANCE':5,
                'INCLUDE_BOUNDS':False,
                'OUTPUT_LINES': this_output
            }
            
            temp_output = processing.run("qgis:serviceareafromlayer", temp_params)['OUTPUT_LINES']
            
            prbVal += 1

        return {self.OUTPUT: temp_output}

    def name(self):
        return 'multipleServiceAreas'

    def displayName(self):
        return self.tr('Multiple Dienstbereiche')

    def group(self):
        return self.tr('Raumanalaysen - Christian Müller')

    def groupId(self):
        return 'Raumanalysen'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return multipleServiceAreas()
