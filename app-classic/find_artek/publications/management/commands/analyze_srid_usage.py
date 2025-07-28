# -*- coding: utf-8 -*-
"""
Django 1.6 management command to analyze SRID usage in Feature geometries.

Usage:
    python manage.py srid_analysis
    python manage.py srid_analysis --sample-size 5
    python manage.py srid_analysis --verbose
    python manage.py srid_analysis --save-to-file
"""

from django.core.management.base import BaseCommand
from optparse import make_option
from collections import Counter
from publications.models import Feature


class Command(BaseCommand):
    help = 'Analyze SRID usage in the Feature model geometry fields'
    
    option_list = BaseCommand.option_list + (
        make_option('--sample-size',
            type='int',
            dest='sample_size',
            default=10,
            help='Number of sample features to display (default: 10)'),
        make_option('--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Show detailed geometry information'),
        make_option('--save-to-file',
            action='store_true',
            dest='save_to_file',
            default=False,
            help='Save results to a text file'),
    )

    def handle(self, *args, **options):
        sample_size = options.get('sample_size', 10)
        verbose = options.get('verbose', False)
        save_to_file = options.get('save_to_file', False)

        self.stdout.write('=== FEATURE SRID ANALYSIS ===\n')

        try:
            # Count total features
            total = Feature.objects.count()
            self.stdout.write("Total features in database: %d" % total)

            # Count features with geometry data
            with_points = Feature.objects.filter(points__isnull=False).count()
            with_lines = Feature.objects.filter(lines__isnull=False).count()
            with_polys = Feature.objects.filter(polys__isnull=False).count()

            self.stdout.write("Features with points: %d" % with_points)
            self.stdout.write("Features with lines: %d" % with_lines)
            self.stdout.write("Features with polygons: %d" % with_polys)

            # Check sample features with points
            if with_points > 0:
                self.stdout.write('\n=== SAMPLE FEATURES WITH POINTS (showing %d) ===' % sample_size)
                sample_features = Feature.objects.filter(points__isnull=False)[:sample_size]
                
                for feature in sample_features:
                    if feature.points:
                        self.stdout.write("Feature ID %d: %s" % (feature.id, feature.name))
                        self.stdout.write("  SRID: %s" % feature.points.srid)
                        if verbose:
                            self.stdout.write("  Geometry type: %s" % feature.points.geom_type)
                            self.stdout.write("  Coordinates: %s" % str(feature.points))
                        self.stdout.write('')

            # Check sample features with lines
            if with_lines > 0:
                sample_count = min(sample_size, 5)
                self.stdout.write('\n=== SAMPLE FEATURES WITH LINES (showing %d) ===' % sample_count)
                sample_features = Feature.objects.filter(lines__isnull=False)[:sample_count]
                
                for feature in sample_features:
                    if feature.lines:
                        self.stdout.write("Feature ID %d: %s" % (feature.id, feature.name))
                        self.stdout.write("  SRID: %s" % feature.lines.srid)
                        if verbose:
                            self.stdout.write("  Geometry type: %s" % feature.lines.geom_type)
                        self.stdout.write('')

            # Check sample features with polygons
            if with_polys > 0:
                sample_count = min(sample_size, 5)
                self.stdout.write('\n=== SAMPLE FEATURES WITH POLYGONS (showing %d) ===' % sample_count)
                sample_features = Feature.objects.filter(polys__isnull=False)[:sample_count]
                
                for feature in sample_features:
                    if feature.polys:
                        self.stdout.write("Feature ID %d: %s" % (feature.id, feature.name))
                        self.stdout.write("  SRID: %s" % feature.polys.srid)
                        if verbose:
                            self.stdout.write("  Geometry type: %s" % feature.polys.geom_type)
                        self.stdout.write('')

            # Get unique SRIDs used in the database
            self.stdout.write('\n=== UNIQUE SRIDs IN USE ===')
            
            # Initialize counters for detailed analysis
            point_srids = Counter()
            line_srids = Counter()
            polygon_srids = Counter()
            
            # For points
            point_features = Feature.objects.filter(points__isnull=False)
            point_srids_set = set()
            for f in point_features:
                if f.points:
                    srid = f.points.srid
                    point_srids_set.add(srid)
                    point_srids[srid] += 1
            self.stdout.write("Point SRIDs used: %s" % str(sorted(point_srids_set)))
            
            # For lines
            line_features = Feature.objects.filter(lines__isnull=False)
            line_srids_set = set()
            for f in line_features:
                if f.lines:
                    srid = f.lines.srid
                    line_srids_set.add(srid)
                    line_srids[srid] += 1
            self.stdout.write("Line SRIDs used: %s" % str(sorted(line_srids_set)))
            
            # For polygons
            poly_features = Feature.objects.filter(polys__isnull=False)
            poly_srids_set = set()
            for f in poly_features:
                if f.polys:
                    srid = f.polys.srid
                    poly_srids_set.add(srid)
                    polygon_srids[srid] += 1
            self.stdout.write("Polygon SRIDs used: %s" % str(sorted(poly_srids_set)))

            # Summary
            all_srids = point_srids_set.union(line_srids_set).union(poly_srids_set)
            self.stdout.write('\n=== SUMMARY ===')
            self.stdout.write("Total unique SRIDs in database: %s" % str(sorted(all_srids)))
            
            if len(all_srids) == 1 and 4326 in all_srids:
                self.stdout.write("* All geometry data uses SRID 4326 (WGS84)")
            elif len(all_srids) > 1:
                self.stdout.write("! Multiple SRIDs detected: %s" % str(sorted(all_srids)))
            else:
                self.stdout.write("X No SRID data found or unexpected SRID")

            # Detailed SRID analysis
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("DETAILED SRID ANALYSIS")
            self.stdout.write("=" * 60)
            
            if all_srids:
                # SRID information lookup
                srid_info = {
                    4326: "WGS 84 (World Geodetic System 1984) - Geographic coordinates",
                    3857: "Web Mercator (Google Maps, OpenStreetMap)",
                    25832: "ETRS89 / UTM zone 32N (Common in Northern Europe)",
                    25833: "ETRS89 / UTM zone 33N (Central Europe)", 
                    32632: "WGS 84 / UTM zone 32N",
                    32633: "WGS 84 / UTM zone 33N",
                    4258: "ETRS89 - European Terrestrial Reference System 1989",
                    2154: "RGF93 / Lambert-93 (France)",
                    28355: "GDA94 / MGA zone 55 (Australia)",
                    31370: "BD72 / Belgian Lambert 72 (Belgium)",
                }
                
                self.stdout.write("\nSRID Information:")
                for srid in sorted(all_srids):
                    info = srid_info.get(srid, "Unknown coordinate system")
                    total_usage = point_srids.get(srid, 0) + line_srids.get(srid, 0) + polygon_srids.get(srid, 0)
                    self.stdout.write("  SRID %s: %s (Used %d times)" % (srid, info, total_usage))

                # Generate recommendations
                if len(all_srids) > 1:
                    most_common_srid = max(all_srids, key=lambda x: 
                                          point_srids.get(x, 0) + line_srids.get(x, 0) + polygon_srids.get(x, 0))
                    self.stdout.write("\nMost commonly used SRID: %s" % most_common_srid)
                    self.stdout.write("\nWarning: Multiple SRIDs detected!")
                    self.stdout.write("Consider standardizing on a single SRID for consistency.")
                    self.stdout.write("You may need to transform geometries to a common coordinate system.")
                    
                    self.stdout.write("\nTo transform geometries, you can use SQL like:")
                    for srid in sorted(all_srids):
                        if srid != most_common_srid:
                            self.stdout.write("  -- Transform SRID %s to %s:" % (srid, most_common_srid))
                            self.stdout.write("  UPDATE publications_feature SET points = ST_Transform(points, %s) WHERE ST_SRID(points) = %s;" % (most_common_srid, srid))
                            self.stdout.write("  UPDATE publications_feature SET lines = ST_Transform(lines, %s) WHERE ST_SRID(lines) = %s;" % (most_common_srid, srid))
                            self.stdout.write("  UPDATE publications_feature SET polys = ST_Transform(polys, %s) WHERE ST_SRID(polys) = %s;" % (most_common_srid, srid))
                else:
                    self.stdout.write("\nGood: All geometries use the same SRID (%s)" % str(list(all_srids)[0]))

            # Save to file if requested
            if save_to_file:
                results = {
                    'point_srids': dict(point_srids),
                    'line_srids': dict(line_srids), 
                    'polygon_srids': dict(polygon_srids),
                    'features_with_points': with_points,
                    'features_with_lines': with_lines,
                    'features_with_polys': with_polys,
                    'total_features': total
                }
                self._save_results_to_file(results)
            
            self.stdout.write('\nSRID analysis completed successfully!')

        except Exception as e:
            self.stdout.write("Error: %s" % str(e))
            import traceback
            self.stdout.write("Traceback:")
            self.stdout.write(traceback.format_exc())

    def _save_results_to_file(self, results):
        """Save analysis results to a JSON file"""
        import json
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = 'srid_analysis_%s.json' % timestamp
        
        # Save to temp directory if it exists, otherwise current directory
        temp_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'temp')
        if os.path.exists(temp_dir):
            filepath = os.path.join(temp_dir, filename)
        else:
            filepath = filename
        
        # Add timestamp to results
        results['analysis_timestamp'] = timestamp
        results['analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            self.stdout.write('\nResults saved to: %s' % filepath)
        except Exception as e:
            self.stdout.write('Warning: Could not save results to file: %s' % str(e))
