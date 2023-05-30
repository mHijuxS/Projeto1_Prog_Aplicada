# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ProgramacaoAplicadaGrupo2
                                 A QGIS plugin
 Solução do Grupo 2
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-05
        copyright            : (C) 2023 by Grupo 2
        email                : matheus.ferreira@ime.eb.br
                               leonardo.fernandes@ime.eb.br
                               daniel.nojima@ime.eb.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Grupo 2'
__date__ = '2023-05-05'
__copyright__ = '(C) 2023 by Grupo 2'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.utils import iface
import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.analysis import QgsNativeAlgorithms
from PyQt5.QtCore import QVariant
from qgis.core import (QgsCoordinateReferenceSystem,
                        QgsFeature,
                        QgsFeatureSink,
                        QgsFields,
                        QgsGeometry,
                        QgsPointXY,
                        QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFeatureSink,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterMultipleLayers,
                        QgsProject,
                        QgsRaster,
                        QgsVectorLayer,
                        QgsField)


class Projeto2SolucaoComplementar(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_MULTILINE = 'INPUT_MULTILINE'
    INPUT_POLYGON = 'INPUT_POLYGON'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_MULTILINE,
                'Input multiline layer',
                [QgsProcessing.TypeVectorLine]))

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_POLYGON,
                'Input polygon layer',
                [QgsProcessing.TypeVectorPolygon]))

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Output multiline layer'))

    def processAlgorithm(self, parameters, context, feedback):
        source_multiline = self.parameterAsSource(parameters, self.INPUT_MULTILINE, context)
        source_polygon = self.parameterAsSource(parameters, self.INPUT_POLYGON, context)

        fields = source_multiline.fields()
        fields.append(QgsField('dentro_de_poligono', QVariant.Bool))

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               fields, source_multiline.wkbType(),
                                               source_multiline.sourceCrs())

        total_features = source_multiline.featureCount()
        processed_features = 0

        for ml_feature in source_multiline.getFeatures():
            geom_ml = ml_feature.geometry()

            inside = False
            for polygon_feature in source_polygon.getFeatures():
                geom_polygon = polygon_feature.geometry()
                if geom_ml.within(geom_polygon):
                    inside = True
                    break

            ml_feature.setAttributes(ml_feature.attributes() + [inside])
            sink.addFeature(ml_feature)

            processed_features += 1
            feedback.setProgress(100.0 * processed_features / total_features)

        return {self.OUTPUT: dest_id}

    def name(self):
        return 'Solução Complementar do Projeto 2'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 2'

    def shortHelpString(self):
        return self.tr("""Esse algoritmo tem como objetivo determinar camadas de vetores do tipo polígono
                          que possuem em seus atributos o nome da camada raster de input, o nome da camada 
                          raster que está sobreposta a ela e o erro relativo entre essas duas camadas, todas
                          agrupadas em um grupo"""
                       )
    
    def tr(self, string):
        return QCoreApplication.translate('Processando', string)

    def createInstance(self):
        return Projeto2SolucaoComplementar()
    
    
    