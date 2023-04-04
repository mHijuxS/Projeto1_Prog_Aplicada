# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ProgramacaoAplicadaGrupo2
                                 A QGIS plugin
 Solução do Grupo 2
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-20
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
__date__ = '2023-03-20'
__copyright__ = '(C) 2023 by Grupo 2'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.utils import iface
import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.analysis import QgsNativeAlgorithms
from PyQt5.QtCore import QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterMultipleLayers,
                       QgsVectorLayer,
                       QgsProject, 
                       QgsGeometry, 
                       QgsPointXY, 
                       QgsField, 
                       QgsFields, 
                       QgsFeature, 
                       QgsCoordinateReferenceSystem, 
                       QgsRaster,
                       QgsProcessingParameterFeatureSink)

class Projeto1SolucaoComplementar(QgsProcessingAlgorithm):
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

    INPUT_LAYERS = 'INPUT_LAYERS'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        # Adicione os parâmetros do CalculateIntersectionBbox
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_LAYERS,
                self.tr('Input Raster Layers'),
                QgsProcessing.TypeRaster
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output Layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Criando a saida agrupada
        group_name = "Saída Script"
        layer_tree_root = QgsProject.instance().layerTreeRoot()
        output_group = layer_tree_root.findGroup(group_name)
        if output_group is None:
            output_group = layer_tree_root.insertGroup(0, group_name)  # Insere o grupo na primeira posição


        layers = self.parameterAsLayerList(parameters, self.INPUT_LAYERS, context)

        # Codigo para processo das camadas
        # os bounding box dos Inputs serao guardados em uma lista
        list = []
        project = QgsProject.instance()
        
        """
        Parte 1: Criando bounding boxes dos rasters 
        """

        for layer in layers: # Percorrendo todos inputs e pegando os seus bounding boxes
            rect = layer.extent()

            polygon_geom = QgsGeometry.fromPolygonXY([[QgsPointXY(rect.xMinimum(),  rect.yMinimum()),
                                                        QgsPointXY(rect.xMinimum(), rect.yMaximum()),
                                                        QgsPointXY(rect.xMaximum(), rect.yMaximum()),
                                                        QgsPointXY(rect.xMaximum(), rect.yMinimum()),
                                                        QgsPointXY(rect.xMinimum(), rect.yMinimum())]]
                                                        )
            new_layer = QgsVectorLayer("Polygon",f"{layer.name()}_BBox",'memory')
            new_layer.setCrs(layer.crs())

            #Criando um campo de atributo chamado 'raster' que vai guardar o raster input de origem na feição da bounding box
            fields = QgsFields()
            fields.append(QgsField('raster',QVariant.String))

            provider = new_layer.dataProvider()
            provider.addAttributes(fields)

            nome = layer.name()
            feature = QgsFeature(new_layer.fields())
            feature.setGeometry(polygon_geom)
            feature.setAttributes([nome])
            provider.addFeature(feature)

            new_layer.updateFields()
            list.append(new_layer)

        """
        Parte 2: Criação das camadas de interseções entre os bounding boxes 
        """

        list2 = list.copy() #copia da lista dos bounding boxes
        # as interseções dos bounding boxes serão guardadas em uma terceira lista
        list3 = []
        project = QgsProject().instance()
        for layer1 in list: # percorrendo todos os bounding boxes da primeira lista
            # removemos a layer1 da lista2 que será percorrida pelo segundo raster de forma a eliminar interseções
            list2.remove(layer1)
            for layer2 in list2:
                # rodamos o processing intersection para pegar as interseções entre as feições
                result = processing.run("qgis:intersection", {
                'INPUT': layer1,
                'OVERLAY': layer2,
                'OUTPUT': 'memory:'
               })
                intersect_layer = result['OUTPUT']
                if not intersect_layer.featureCount()==0:
                    list3.append(intersect_layer) # guardamos as interseções das feições em uma lista 3 

        """
        Parte 3: Criação do grid de pontos espaçados 
        """

        # Os outputs serão guardados em uma lista results
        result = []
        
        # Para cada camada na lista 3, criamos um grid de pontos espaçados 200m em x e y na extensão dessa camada
        for layer in list3:
            extent = layer.extent()

            resultado = processing.run("native:creategrid", {'TYPE':0,
            'EXTENT':extent,
            'HSPACING':200,
            'VSPACING':200,
            'HOVERLAY':0,
            'VOVERLAY':0,
            'CRS':QgsCoordinateReferenceSystem('EPSG:31982'),
            'OUTPUT':'TEMPORARY_OUTPUT'})

            result.append(resultado['OUTPUT'])


        """
        Parte 4: Calculo do erro, gerando as camadas com os outputs desejados, agrupando em um grupo os outputs e adicionando no projeto
        """

        # para cada camada na lista 3, percorre-se as feições adicionando o campo de atributos 'Eqz' com o erro calculado no final do algoritmo
        for intersect in list3:
            new_field = QgsField('Eqz',QVariant.Double)
            intersect_provider = intersect.dataProvider()
            intersect_provider.addAttributes([new_field])
            intersect.updateFields()
            erro = 0
            counter = 0
            intersect.startEditing()
            # para cada feição da camada da lista 3, comparamos os valores dos rasters no mesmo x e y do grid anterior e armazenamos o resultado em erro e depois adicionamos o eqm no campo eqz da feição 
            for feat in intersect.getFeatures():
                raster1 = project.mapLayersByName(feat.attributes()[0])[0]
                raster2 = project.mapLayersByName(feat.attributes()[1])[0]
                provider1 = raster1.dataProvider()
                provider2 = raster2.dataProvider()
                for layer_point in result:
                    for point_feat in layer_point.getFeatures():
                        if intersect.extent().contains(point_feat.geometry().boundingBox()):
                            geom = point_feat.geometry()
                            x,y = geom.asPoint()
                            point = QgsPointXY(x,y)
                            pixel_value1 = provider1.identify(point,QgsRaster.IdentifyFormatValue).results()[1]
                            pixel_value2 = provider2.identify(point,QgsRaster.IdentifyFormatValue).results()[1]
                            erro = abs(pixel_value1 - pixel_value2)
                            erro = erro + erro**2
                            counter = counter + 1
                EMQz = (erro/counter)**1/2
                feat[2] = EMQz
                intersect.updateFeature(feat)
            intersect.commitChanges()
            temp = intersect
            # mudamos o nome da camada para os rasters em que elas foram comparados dois a dois
            temp.setName(f"{feat.attributes()[0]}_{feat.attributes()[1]}")
            layer_tree_layer = project.addMapLayer(temp, False)
            
            # adicionamos a camada no projeto 
            output_group.addLayer(temp) 
        # The current implementation does not process layers and will return an empty layer.
        
        # Create an empty memory layer as output
        output_layer = temp

        return {}

    def name(self):
        return 'Solução Complementar do Projeto 1'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Projeto 1'

    def tr(self, string):
        return QCoreApplication.translate('Processando', string)

    def createInstance(self):
        return Projeto1SolucaoComplementar()
    
    
    