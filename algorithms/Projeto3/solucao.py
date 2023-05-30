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

import os
import processing

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber, QgsProcessingParameterVectorLayer,
                       QgsProject,
                       QgsField,
                       QgsFeatureSink,
                       QgsCoordinateReferenceSystem,
                       QgsVectorLayer,
                       QgsFields,
                       QgsGeometry,
                       QgsPointXY,
                       QgsFeature,
                       QgsRaster)


class Projeto3Solucao(QgsProcessingAlgorithm):

    def processAlgorithm(self, parameters, context, feedback):
        buildingsLayer, highwaysLayer, maxDisplacementDistance = self.getParameters(parameters, context)
        output_sink, output_dest_id = self.createOutputSink(parameters, context, buildingsLayer)
        self.processBuildings(buildingsLayer, highwaysLayer, maxDisplacementDistance, output_sink, feedback)
        self.configureOutputLayerStyle(output_dest_id, context, feedback)
        return {self.OUTPUT: output_dest_id}

    def configureOutputLayerStyle(self, output_dest_id, context, feedback):
        set_wd = os.path.dirname(__file__)
        style = os.path.join(set_wd, 'edificacoes.qml')
        alg_params = {
            'INPUT': output_dest_id,
            'STYLE': style 
        }
        processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

    def name(self):
        return 'Projeto3Solucao'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 3'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto3Solucao()

