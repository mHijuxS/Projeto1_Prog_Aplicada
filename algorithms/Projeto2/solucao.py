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

import pandas as pd
import geopandas as gpd

from qgis import processing
from qgis.utils import iface
from PyQt5.QtCore import QVariant
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProject,
                       QgsWkbTypes,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingUtils,
                       QgsVectorLayer,
                       QgsFeatureSink,
                       QgsExpression,
                       QgsSpatialIndex,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterRasterLayer,
                       QgsVectorFileWriter,
                       QgsCoordinateTransform,
                       QgsWkbTypes,
                       QgsGeometry,
                       QgsPointXY,
                       QgsFields,
                       QgsFeature,
                       QgsField,
                       QgsRaster,
                       QgsMarkerSymbol,
                       QgsCategorizedSymbolRenderer,
                       QgsRendererCategory,
                       QgsSymbol,
                       QgsProcessingParameterFeatureSink
                    )


class Projeto2Solucao(QgsProcessingAlgorithm):

    """
    Definindo as constantes
    """
    
    # INPUTS 
    INPUT_DRAINAGES = 'INPUT_DRAINAGES'
    INPUT_SINK_SPILL = 'INPUT_SINK_SPILL'
    INPUT_WATER_BODY = 'INPUT_WATER'
    INPUT_CANAL = 'INPUT_CANAL'

    # OUTPUTS
    POINTFLAGS = 'POINTFLAGS'
    LINEFLAGS = 'LINEFLAGS'
    POLYGONFLAGS = 'POLYGONFLAGS'
      
    def initAlgorithm(self, config=None):

        #INPUTS
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_DRAINAGES, 
                                                            'Drenagens',
                                                            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_SINK_SPILL, 
                                                            'Sumidouros e Vertedouros', 
                                                             types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_CANAL, 
                                                            'Canais', 
                                                             types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_WATER_BODY, 
                                                            'Massa de Agua', 
                                                            types=[QgsProcessing.TypeVectorPolygon]))
        
        #OUTPUTS
        self.addParameter(QgsProcessingParameterFeatureSink(self.POINTFLAGS, 'Erros pontuais'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.LINEFLAGS, 'Erros em linhas'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.POLYGONFLAGS, 'Erros em polígonos'))


  
      
    def processAlgorithm(self, parameters, context, feedback):
        #Store the input variables
        drains = self.parameterAsSource(parameters,
                                        self.INPUT_DRAINAGES,
                                        context)
        sink_spills_points = self.parameterAsSource(parameters,
                                                    self.INPUT_SINK_SPILL,
                                                    context)
        water_body = self.parameterAsSource(parameters,
                                            self.INPUT_WATER_BODY,
                                            context)
        canals = self.parameterAsSource(parameters,
                                        self.INPUT_CANAL,
                                        context)
        
        #Separating Water Bodies with and without flux of water
        # Defining the Water Body with flow and without flow
        ## Without Flow
        water_body_no_flow = QgsVectorLayer(water_body.source(), 'water_body_no_flow', water_body.providerType())
        filter = QgsExpression('possuitrechodrenagem = 0')
        water_body_no_flow.setSubsetString(filter.expression())

        ## With Flow 
        water_body_with_flow = QgsVectorLayer(water_body.source(), 'water_body_with_flow', water_body.providerType())
        filter = QgsExpression('possuitrechodrenagem = 1')
        water_body_with_flow.setSubsetString(filter.expression())
        
        #Applying the same logic for the Sink and Spill Points
        sink_points = QgsVectorLayer(sink_spills_points.source(), 'sink_points', sink_spills_points.providerType())
        filter = QgsExpression('tiposumvert = 1')
        sink_points.setSubsetString(filter.expression())

        spill_points = QgsVectorLayer(sink_spills_points.source(), 'spill_points', sink_spills_points.providerType())
        filter = QgsExpression('tiposumvert = 2')
        spill_points.setSubsetString(filter.expression())


        # Outputs terão um campo de atributo explicando a razão da flag
        fields = QgsFields()
        fields.append(QgsField("Motivo", QVariant.String))

        # Configurando os Outputs 
        (sink_point, dest_id_point) = self.parameterAsSink(parameters,
                                                           self.POINTFLAGS,
                                                           context,
                                                           fields,
                                                           QgsWkbTypes.Point,
                                                           drains.sourceCrs()
                                                           )
        
        (sink_line, dest_id_line) = self.parameterAsSink(parameters,
                                                         self.LINEFLAGS,
                                                         context,
                                                         fields,
                                                         QgsWkbTypes.LineString,
                                                         drains.sourceCrs()
                                                         ) 

        (sink_polygon, dest_id_polygon) = self.parameterAsSink(parameters,
                                                               self.POLYGONFLAGS,
                                                               context,
                                                               fields,
                                                               QgsWkbTypes.Polygon,
                                                               drains.sourceCrs()
                                                               )
        
        
        

        
        # Calculando a estrutura das linhas
        pointInAndOutDictionary = {}

        lineCount = drains.featureCount()
        multiStepFeedback = QgsProcessingMultiStepFeedback(2, feedback)
        multiStepFeedback.setCurrentStep(0)
        multiStepFeedback.setProgressText(self.tr("Calculando a estrutura das Linhas..."))
        stepSize = 100/lineCount

        # Adicionando ao dicionário a quantidade de linhas que entram e saem de um determinado ponto
        for current, line in enumerate(drains.getFeatures()):
            if multiStepFeedback.isCanceled():
                break
            geom = list(line.geometry().vertices())
            if len(geom) == 0:
                continue
            first_vertex = geom[0]
            last_vertex = geom[-1]

            if first_vertex.asWkt() not in pointInAndOutDictionary:
                pointInAndOutDictionary[first_vertex.asWkt()] = { "incoming": 0, "outgoing": 0}

            if last_vertex.asWkt() not in pointInAndOutDictionary:
                pointInAndOutDictionary[last_vertex.asWkt()] = { "incoming": 0, "outgoing": 0}
            
            pointInAndOutDictionary[first_vertex.asWkt()]["outgoing"] += 1
            pointInAndOutDictionary[last_vertex.asWkt()]["incoming"] += 1
            multiStepFeedback.setProgress(current * stepSize)
        
        multiStepFeedback.setCurrentStep(1)
                
   ###############################################################################################
   ######################################### ITEM 1 ##############################################    
   ###############################################################################################



   ###############################################################################################
   ###################################### ITEM 2 e 3 #############################################    
   ###############################################################################################

    #Iterando sobre o dicionario e vendo se algum dos pontos do tipo sumidouro estão no caso em que
    #"Incoming = 0" e "Outgoing = 1"
        for point in sink_spills_points.getFeatures():
            sink_type = point.attributes()[4]
            if sink_type != 1:
                continue
            for (point_wkt,in_out) in pointInAndOutDictionary.items():
                if (in_out["incoming"] ==0 and in_out["outgoing"] == 1):
                    if point.geometry().equals(QgsGeometry.fromWkt(point_wkt)):
                        flag = QgsFeature(fields)
                        flag.setGeometry(QgsGeometry.fromWkt(point.geometry().asWkt()))
                        flag["Motivo"] = "Não pode ser um Sumidouro"
                        sink_point.addFeature(flag)
    #Mesma Lógica para "Incoming=1" e "Outgoing = 0"
        for point in sink_spills_points.getFeatures():
            sink_type = point.attributes()[4]
            if sink_type != 2:
                continue
            for (point_wkt,in_out) in pointInAndOutDictionary.items():
                if (in_out["incoming"] ==1 and in_out["outgoing"] == 0):
                    if point.geometry().equals(QgsGeometry.fromWkt(point_wkt)):
                        flag = QgsFeature(fields)
                        flag.setGeometry(QgsGeometry.fromWkt(point.geometry().asWkt()))
                        flag["Motivo"] = "Não pode ser um Vertedouro"
                        sink_point.addFeature(flag)

   # TO DO
   #################################### ITEM 4 ############################################    
   ###############################################################################################

   ###############################################################################################
   ######################################### ITEM 7 ##############################################    
   ###############################################################################################

        self.find_canals_connected_to_drains(canals, drains, feedback) 

   ##############################################################################################
   ######################################## ITEM 8 ##############################################    
   ###############################################################################################      
        #Todos os vertedouros e sumidouros deveriam estar no dicionário de pontos que entram e saem drenagens
        #Portanto, basta verificar se estão ou não 
        
        attributesError = 0
        for ponto in sink_spills_points.getFeatures():
            pontoGeometry = ponto.geometry()
            nome = ponto.attributes()[1]
            noError = False
            for line in drains.getFeatures():
                lineGeometry = line.geometry()
                for part in lineGeometry.parts():
                    vertices = list(part)
                    for i in range(len(vertices)-1):
                        point = QgsGeometry.fromPointXY(QgsPointXY(vertices[i].x(), vertices[i].y()))
                        if pontoGeometry.intersects(point): noError = True
            if noError:
                feedback.pushInfo(f"O sumidouro/vertedouro {nome} está isolado.")
                flag = QgsFeature(fields)
                flag.setGeometry(QgsGeometry.asPoint(point))
                flag["Motivo"] = "O sumidouro/vertedouro está isolado"
                sink_point.addFeature(flag)
                attributesError += 1

                    
        return {self.POINTFLAGS: dest_id_point,
                self.LINEFLAGS: dest_id_line,
                self.POLYGONFLAGS: dest_id_polygon} 
        
    def tr(self, string):
        return QCoreApplication.translate('Processando', string)

    def createInstance(self):
        return Projeto2Solucao()

    def name(self):
        return 'Solução do Projeto 2'

    def displayName(self):
        return self.tr(self.name())

    def group(self):        
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 2'
        
    def shortHelpString(self):
        return self.tr("""ESCREVER AQUI"""
                       )
    
    """ 

    FUNÇÕES AUXILIARES

    """  
    def find_canals_connected_to_drains(self,canals_layer, drains_layer, feedback):
        # Verifica se as camadas são válidas:
        if not canals_layer.isValid() or not drains_layer.isValid():
            raise ValueError("Camadas inválidas")

        # Cria um dicionário para armazenar os índices espaciais dos canais e suas geometrias:
        canal_geometries = {}
        canal_spatial_index = QgsSpatialIndex()

        for canal_feat in canals_layer.getFeatures():
            canal_geom = canal_feat.geometry()
            canal_geometries[canal_feat.id()] = canal_geom
            canal_spatial_index.addFeature(canal_feat)

        # Inicializa uma lista para armazenar os índices dos canais conectados às drenagens:
        connected_canal_ids = []

        # Itera sobre as feições das drenagens:
        for drain_feat in drains_layer.getFeatures():
            drain_geom = drain_feat.geometry()
            bbox_drain = drain_geom.boundingBox()

            # Itera sobre os índices espaciais dos canais que intersectam a bounding box da drenagem:
            for canal_id in canal_spatial_index.intersects(bbox_drain):
                canal_geom = canal_geometries[canal_id]

                # Verifica se a geometria do canal é igual à geometria da drenagem:
                if drain_geom.equals(canal_geom):
                    connected_canal_ids.append(canal_id)

            # Atualiza o feedback de progresso:
            feedback.setProgressText(f"Processando drenagem {drain_feat.id()}")
            feedback.setProgress(int(drain_feat.id() / drains_layer.featureCount() * 100))

        return connected_canal_ids