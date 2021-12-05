from django.db import models

# Create your models here.

class Drug(models.Model):
    drugid = models.IntegerField(primary_key=True)
    drugname = models.CharField(max_length=30)
    isopioid = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'drug'
    
    def __str__(self):
        return (self.drugname)

class State(models.Model):
    state = models.CharField(primary_key=True, max_length=2)
    statename = models.CharField(max_length=50)
    population = models.IntegerField()
    deaths = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'state'
    
    def __str__(self):
        return (self.statename)

class Prescriber(models.Model):
    npi = models.IntegerField(primary_key=True)
    fname = models.CharField(max_length=11)
    lname = models.CharField(max_length=11)
    gender = models.CharField(max_length=1)
    state = models.ForeignKey(State, models.DO_NOTHING, db_column='state')
    specialty = models.CharField(max_length=62)
    isopioidprescriber = models.BooleanField()
    totalprescriptions = models.IntegerField()
    credential = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'prescriber'
    
    def __str__(self):
        return (self.lname + ", " + self.fname)

class Prescriberdrug(models.Model):
    npi = models.OneToOneField(Prescriber, models.DO_NOTHING, db_column='npi', primary_key=True)
    drugid = models.ForeignKey(Drug, models.DO_NOTHING, db_column='drugid')
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prescriberdrug'
        unique_together = (('npi', 'drugid'),)
    
    def __str__(self):
        return (str(self.npi) + ": " + str(self.drugid) + ": " + str(self.quantity))
